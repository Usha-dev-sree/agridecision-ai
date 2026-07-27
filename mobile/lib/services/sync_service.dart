import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../database/local_database.dart';

class SyncService {
  final Dio _dio;
  final LocalDatabase _localDb = LocalDatabase.instance;
  bool _isSyncing = false;

  SyncService(this._dio) {
    // Monitor connectivity changes to trigger automatic sync
    Connectivity().onConnectivityChanged.listen((ConnectivityResult result) {
      if (result != ConnectivityResult.none) {
        triggerSync();
      }
    });
  }

  Future<void> triggerSync() async {
    if (_isSyncing) return;
    _isSyncing = true;

    try {
      final queued = await _localDb.getQueuedRequests();
      for (final req in queued) {
        final id = req['id'] as int;
        final endpoint = req['endpoint'] as String;
        final method = req['method'] as String;
        final payload = jsonDecode(req['payload'] as String);

        try {
          Response response;
          if (method == 'POST') {
            response = await _dio.post(endpoint, data: payload);
          } else if (method == 'PATCH') {
            response = await _dio.patch(endpoint, data: payload);
          } else if (method == 'PUT') {
            response = await _dio.put(endpoint, data: payload);
          } else if (method == 'DELETE') {
            response = await _dio.delete(endpoint);
          } else {
            continue;
          }

          if (response.statusCode != null && response.statusCode! >= 200 && response.statusCode! < 300) {
            await _localDb.deleteQueuedRequest(id);
          }
        } on DioException catch (e) {
          // If server fails or connection breaks again, halt queue processing
          if (e.type != DioExceptionType.badResponse) {
            break;
          }
        }
      }
    } finally {
      _isSyncing = false;
    }
  }

  // Synchronize remote plots to local database (pull replication)
  Future<void> pullRemoteData() async {
    try {
      final response = await _dio.get('/v1/plots');
      if (response.statusCode == 200) {
        final plotsList = response.data as List;
        for (final p in plotsList) {
          final plotMap = p as Map<String, dynamic>;
          await _localDb.savePlot({
            'id': plotMap['id'],
            'name': plotMap['name'],
            'total_area_ha': plotMap['total_area_ha'],
            'irrigation_type': plotMap['irrigation_type'],
            'centroid_lat': plotMap['centroid_lat'],
            'centroid_lng': plotMap['centroid_lng'],
            'is_active': plotMap['is_active'] == true ? 1 : 0,
            'sync_status': 'SYNCED',
          });

          // Fetch soil profiles for plot
          try {
            final soilRes = await _dio.get('/v1/plots/${plotMap['id']}/soil');
            if (soilRes.statusCode == 200) {
              final soilMap = soilRes.data as Map<String, dynamic>;
              await _localDb.saveSoilProfile({
                'plot_id': plotMap['id'],
                'soil_type': soilMap['soil_type'],
                'texture_class': soilMap['texture_class'],
                'ph_level': soilMap['ph_level'],
                'nitrogen_content': soilMap['nitrogen_content'],
                'phosphorus_content': soilMap['phosphorus_content'],
                'potassium_content': soilMap['potassium_content'],
                'organic_carbon_percent': soilMap['organic_carbon_percent'],
                'sync_status': 'SYNCED',
              });
            }
          } catch (_) {}
        }
      }
    } catch (_) {}
  }
}
