import 'dart:async';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class LocalDatabase {
  static final LocalDatabase instance = LocalDatabase._init();
  static Database? _database;

  LocalDatabase._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('agridecision.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future<void> _createDB(Database db, int version) async {
    // 1. Plots Table
    await db.execute('''
      CREATE TABLE plots (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        total_area_ha REAL NOT NULL,
        irrigation_type TEXT NOT NULL,
        centroid_lat REAL,
        centroid_lng REAL,
        is_active INTEGER NOT NULL DEFAULT 1,
        sync_status TEXT NOT NULL DEFAULT 'SYNCED'
      )
    ''');

    // 2. Soil Profiles Table
    await db.execute('''
      CREATE TABLE soil_profiles (
        plot_id TEXT PRIMARY KEY,
        soil_type TEXT,
        texture_class TEXT,
        ph_level REAL,
        nitrogen_content REAL,
        phosphorus_content REAL,
        potassium_content REAL,
        organic_carbon_percent REAL,
        sync_status TEXT NOT NULL DEFAULT 'SYNCED'
      )
    ''');

    // 3. Crop Seasons Table
    await db.execute('''
      CREATE TABLE crop_seasons (
        id TEXT PRIMARY KEY,
        plot_id TEXT NOT NULL,
        crop_name TEXT NOT NULL,
        season_name TEXT NOT NULL,
        status TEXT NOT NULL,
        sowing_date TEXT,
        expected_harvest_date TEXT,
        sync_status TEXT NOT NULL DEFAULT 'SYNCED'
      )
    ''');

    // 4. Offline Sync Queue Table
    await db.execute('''
      CREATE TABLE sync_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT NOT NULL,
        method TEXT NOT NULL,
        payload TEXT NOT NULL,
        timestamp TEXT NOT NULL
      )
    ''');
  }

  // Helper inserts and queries
  Future<void> savePlot(Map<String, dynamic> plot) async {
    final db = await database;
    await db.insert('plots', plot, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Map<String, dynamic>>> getPlots() async {
    final db = await database;
    return await db.query('plots', where: 'is_active = 1');
  }

  Future<void> saveSoilProfile(Map<String, dynamic> soil) async {
    final db = await database;
    await db.insert('soil_profiles', soil, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<Map<String, dynamic>?> getSoilProfile(String plotId) async {
    final db = await database;
    final results = await db.query('soil_profiles', where: 'plot_id = ?',   whereArgs: [plotId]);
    return results.isNotEmpty ? results.first : null;
  }

  Future<void> saveCropSeason(Map<String, dynamic> season) async {
    final db = await database;
    await db.insert('crop_seasons', season, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Map<String, dynamic>>> getCropSeasons(String plotId) async {
    final db = await database;
    return await db.query('crop_seasons', where: 'plot_id = ?', whereArgs: [plotId]);
  }

  // Offline Sync Queue Management
  Future<void> queueRequest(String endpoint, String method, String payload) async {
    final db = await database;
    await db.insert('sync_queue', {
      'endpoint': endpoint,
      'method': method,
      'payload': payload,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  Future<List<Map<String, dynamic>>> getQueuedRequests() async {
    final db = await database;
    return await db.query('sync_queue', orderBy: 'id ASC');
  }

  Future<void> deleteQueuedRequest(int id) async {
    final db = await database;
    await db.delete('sync_queue', where: 'id = ?', whereArgs: [id]);
  }
}
