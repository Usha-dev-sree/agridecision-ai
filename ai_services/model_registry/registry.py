"""
Model Registry
Defines database schemas and management helper classes to record model files,
version history, deployment status, and evaluation metrics.
Supports a built-in sqlite3 fallback when SQLAlchemy is not installed in the environment.
"""
import os
import datetime
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

try:
    from sqlalchemy import (
        Column,
        DateTime,
        Float,
        ForeignKey,
        Integer,
        String,
        Text,
        create_engine,
    )
    from sqlalchemy.orm import declarative_base, relationship, sessionmaker
    HAS_SQLALCHEMY = True
    Base = declarative_base()
except ImportError:
    HAS_SQLALCHEMY = False
    Base = object # type: ignore


if HAS_SQLALCHEMY:
    class RegisteredModel(Base): # type: ignore
        __tablename__ = "registered_models"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(100), unique=True, nullable=False)
        description = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)

        versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")


    class ModelVersion(Base): # type: ignore
        __tablename__ = "model_versions"

        id = Column(Integer, primary_key=True, autoincrement=True)
        model_id = Column(Integer, ForeignKey("registered_models.id"), nullable=False)
        version = Column(String(50), nullable=False)
        status = Column(String(50), default="staging")  # staging, production, archived
        framework = Column(String(50), nullable=False)  # pytorch, xgboost, lightgbm, scikit-learn
        artifact_path = Column(String(500), nullable=False)  # path to ONNX file
        created_at = Column(DateTime, default=datetime.datetime.utcnow)

        model = relationship("RegisteredModel", back_populates="versions")
        metrics = relationship("ModelMetric", back_populates="version_ref", cascade="all, delete-orphan")


    class ModelMetric(Base): # type: ignore
        __tablename__ = "model_metrics"

        id = Column(Integer, primary_key=True, autoincrement=True)
        version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False)
        metric_name = Column(String(100), nullable=False)
        metric_value = Column(Float, nullable=False)

        version_ref = relationship("ModelVersion", back_populates="metrics")


class ModelRegistryManager:
    """Manages registering and querying models. Combines SQLAlchemy and raw sqlite3 fallbacks."""

    def __init__(self, database_url: str = "sqlite:///c:/AGRICULTURE PROJECT/agridecision-ai/ai_services/model_registry/registry.db") -> None:
        self.database_url = database_url
        
        # Parse db file path
        if database_url.startswith("sqlite:///"):
            self.db_path = database_url.replace("sqlite:///", "")
        else:
            self.db_path = "c:/AGRICULTURE PROJECT/agridecision-ai/ai_services/model_registry/registry.db"
            
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if HAS_SQLALCHEMY:
            connect_args = {"timeout": 30} if database_url.startswith("sqlite") else {}
            self.engine = create_engine(database_url, connect_args=connect_args)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger_info = "Initialized Model Registry using SQLAlchemy."
        else:
            # Direct SQLite tables initialization
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registered_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id INTEGER NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    artifact_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(model_id) REFERENCES registered_models(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    FOREIGN KEY(version_id) REFERENCES model_versions(id)
                )
            """)
            conn.commit()
            conn.close()
            logger_info = "Initialized Model Registry using sqlite3 fallback (SQLAlchemy missing)."
        
        print(logger_info)

    def register_model(self, name: str, description: Optional[str] = None) -> int:
        """Register a new model entity name."""
        if HAS_SQLALCHEMY:
            session = self.Session()
            try:
                model = session.query(RegisteredModel).filter_by(name=name).first()
                if not model:
                    model = RegisteredModel(name=name, description=description)
                    session.add(model)
                    session.commit()
                return model.id
            finally:
                session.close()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM registered_models WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                model_id = row[0]
            else:
                now_str = datetime.datetime.utcnow().isoformat()
                cursor.execute(
                    "INSERT INTO registered_models (name, description, created_at) VALUES (?, ?, ?)",
                    (name, description, now_str)
                )
                conn.commit()
                model_id = cursor.lastrowid
            conn.close()
            return model_id

    def log_version(
        self,
        model_name: str,
        version: str,
        framework: str,
        artifact_path: str,
        metrics: Dict[str, float],
        status: str = "staging"
    ) -> int:
        """Log a new trained version binary of a model along with evaluation metrics."""
        model_id = self.register_model(model_name)
        
        if HAS_SQLALCHEMY:
            session = self.Session()
            try:
                if status == "production":
                    existing_prod = session.query(ModelVersion).filter_by(model_id=model_id, status="production").all()
                    for ep in existing_prod:
                        ep.status = "archived"

                mv = ModelVersion(
                    model_id=model_id,
                    version=version,
                    status=status,
                    framework=framework,
                    artifact_path=artifact_path
                )
                session.add(mv)
                session.flush()

                for m_name, m_val in metrics.items():
                    met = ModelMetric(version_id=mv.id, metric_name=m_name, metric_value=m_val)
                    session.add(met)

                session.commit()
                return mv.id
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                if status == "production":
                    cursor.execute(
                        "UPDATE model_versions SET status = 'archived' WHERE model_id = ? AND status = 'production'",
                        (model_id,)
                    )
                
                now_str = datetime.datetime.utcnow().isoformat()
                cursor.execute(
                    "INSERT INTO model_versions (model_id, version, status, framework, artifact_path, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (model_id, version, status, framework, artifact_path, now_str)
                )
                version_id = cursor.lastrowid
                
                for m_name, m_val in metrics.items():
                    cursor.execute(
                        "INSERT INTO model_metrics (version_id, metric_name, metric_value) VALUES (?, ?, ?)",
                        (version_id, m_name, m_val)
                    )
                conn.commit()
                return version_id
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def get_latest_version(self, model_name: str, status: Optional[str] = "production") -> Optional[Dict[str, Any]]:
        """Retrieve model metadata, artifact path, and performance metrics for the active version."""
        if HAS_SQLALCHEMY:
            session = self.Session()
            try:
                query = session.query(ModelVersion).join(RegisteredModel).filter(RegisteredModel.name == model_name)
                if status:
                    query = query.filter(ModelVersion.status == status)

                mv = query.order_by(ModelVersion.created_at.desc()).first()
                if not mv:
                    if status == "production":
                        return self.get_latest_version(model_name, status=None)
                    return None

                return {
                    "model_name": model_name,
                    "version": mv.version,
                    "status": mv.status,
                    "framework": mv.framework,
                    "artifact_path": mv.artifact_path,
                    "metrics": {m.metric_name: m.metric_value for m in mv.metrics},
                    "created_at": mv.created_at.isoformat()
                }
            finally:
                session.close()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                if status:
                    cursor.execute(
                        "SELECT mv.id, mv.version, mv.status, mv.framework, mv.artifact_path, mv.created_at "
                        "FROM model_versions mv JOIN registered_models rm ON mv.model_id = rm.id "
                        "WHERE rm.name = ? AND mv.status = ? ORDER BY mv.created_at DESC LIMIT 1",
                        (model_name, status)
                    )
                else:
                    cursor.execute(
                        "SELECT mv.id, mv.version, mv.status, mv.framework, mv.artifact_path, mv.created_at "
                        "FROM model_versions mv JOIN registered_models rm ON mv.model_id = rm.id "
                        "WHERE rm.name = ? ORDER BY mv.created_at DESC LIMIT 1",
                        (model_name,)
                    )
                row = cursor.fetchone()
                if not row:
                    if status == "production":
                        conn.close()
                        return self.get_latest_version(model_name, status=None)
                    conn.close()
                    return None
                
                version_id, version_num, stat, framework, art_path, created = row
                
                # Fetch metrics
                cursor.execute(
                    "SELECT metric_name, metric_value FROM model_metrics WHERE version_id = ?",
                    (version_id,)
                )
                metrics = {r[0]: r[1] for r in cursor.fetchall()}
                
                return {
                    "model_name": model_name,
                    "version": version_num,
                    "status": stat,
                    "framework": framework,
                    "artifact_path": art_path,
                    "metrics": metrics,
                    "created_at": created
                }
            finally:
                conn.close()

    def update_status(self, model_name: str, version: str, status: str) -> bool:
        """Promote or demote a model version's deployment status."""
        if HAS_SQLALCHEMY:
            session = self.Session()
            try:
                model = session.query(RegisteredModel).filter_by(name=model_name).first()
                if not model:
                    return False

                mv = session.query(ModelVersion).filter_by(model_id=model.id, version=version).first()
                if not mv:
                    return False

                if status == "production":
                    others = session.query(ModelVersion).filter(
                        ModelVersion.model_id == model.id,
                        ModelVersion.status == "production",
                        ModelVersion.id != mv.id
                    ).all()
                    for oth in others:
                        oth.status = "archived"

                mv.status = status
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id FROM registered_models WHERE name = ?", (model_name,))
                m_row = cursor.fetchone()
                if not m_row:
                    return False
                model_id = m_row[0]
                
                cursor.execute("SELECT id FROM model_versions WHERE model_id = ? AND version = ?", (model_id, version))
                v_row = cursor.fetchone()
                if not v_row:
                    return False
                version_id = v_row[0]
                
                if status == "production":
                    cursor.execute(
                        "UPDATE model_versions SET status = 'archived' WHERE model_id = ? AND status = 'production' AND id != ?",
                        (model_id, version_id)
                    )
                
                cursor.execute("UPDATE model_versions SET status = ? WHERE id = ?", (status, version_id))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
