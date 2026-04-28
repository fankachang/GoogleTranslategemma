import time
import uuid
from typing import Dict, Optional
import asyncio


class SessionManager:
    """
    會話管理器：追蹤線上使用者。
    
    會話機制：
    - 前端 connect：建立新會話，傳回 session_id
    - 前端 heartbeat：定期發送心跳以更新最後活躍時間
    - 前端 disconnect：明確關閉會話
    - 後端自動清理：超過逾時時間（預設 15 分鐘）的會話自動移除
    """
    
    def __init__(self, session_timeout_seconds: int = 900):
        """
        初始化會話管理器。
        
        Args:
            session_timeout_seconds: 會話逾時秒數，超過此時間未有活動則自動移除
        """
        self.session_timeout_seconds = session_timeout_seconds
        self.sessions: Dict[str, Dict] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def connect(self) -> str:
        """
        建立新會話。
        
        Returns:
            新會話的 session_id
        """
        session_id = str(uuid.uuid4())
        now = time.time()
        self.sessions[session_id] = {
            "created_at": now,
            "last_heartbeat": now,
            "user_agent": None,
        }
        return session_id
    
    def heartbeat(self, session_id: str) -> bool:
        """
        更新會話的最後活躍時間（心跳）。
        
        Args:
            session_id: 會話 ID
            
        Returns:
            會話是否存在且成功更新
        """
        if session_id not in self.sessions:
            return False
        
        self.sessions[session_id]["last_heartbeat"] = time.time()
        return True
    
    def disconnect(self, session_id: str) -> bool:
        """
        明確關閉會話。
        
        Args:
            session_id: 會話 ID
            
        Returns:
            會話是否存在且成功移除
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_online_count(self) -> int:
        """取得當前線上使用者數量。"""
        return len(self.sessions)
    
    def cleanup_expired(self) -> int:
        """
        清理已過期的會話。
        
        Returns:
            被清理的會話數量
        """
        now = time.time()
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if now - session["last_heartbeat"] > self.session_timeout_seconds
        ]
        
        for sid in expired_ids:
            del self.sessions[sid]
        
        return len(expired_ids)
    
    async def start_cleanup_task(self, check_interval_seconds: int = 60):
        """
        啟動定期清理任務。
        
        Args:
            check_interval_seconds: 清理檢查間隔秒數
        """
        async def _cleanup():
            while True:
                try:
                    await asyncio.sleep(check_interval_seconds)
                    cleaned = self.cleanup_expired()
                    if cleaned > 0:
                        print(f"[SessionManager] 清理 {cleaned} 個過期會話")
                except asyncio.CancelledError:
                    raise
                except Exception as e:  # noqa: BLE001
                    print(f"[SessionManager] 清理出錯: {e}")
        
        self._cleanup_task = asyncio.create_task(_cleanup())
    
    async def stop_cleanup_task(self):
        """停止清理任務。"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
