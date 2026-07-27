"""
Farm Service - gRPC Server
Exposes high-performance internal endpoints for cross-service communication.
"""
import asyncio
from concurrent import futures
from typing import Any

# In a real implementation, this would import from compiled protobuf files
# import grpc
# from backend.services.farm_service.src.grpc import farm_pb2, farm_pb2_grpc

from backend.common.logging import get_logger

logger = get_logger(__name__)

class FarmServiceServicer: # (farm_pb2_grpc.FarmServiceServicer):
    """
    gRPC Servicer for the Farm Service.
    Used by the Advisory Service for fast retrieval of plot coordinates and soil data
    to run ML models.
    """
    def __init__(self, db_manager: Any):
        self.db_manager = db_manager

    # async def GetPlotDetails(self, request, context):
    #     logger.info("gRPC GetPlotDetails called", extra={"plot_id": request.plot_id})
    #     # Fetch from DB and return protobuf response
    #     return farm_pb2.PlotResponse(...)

async def serve_grpc(db_manager: Any, port: int = 50051) -> None:
    """Start the gRPC server."""
    # server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    # farm_pb2_grpc.add_FarmServiceServicer_to_server(FarmServiceServicer(db_manager), server)
    # server.add_insecure_port(f'[::]:{port}')
    # await server.start()
    # logger.info(f"gRPC server started on port {port}")
    # await server.wait_for_termination()
    pass
