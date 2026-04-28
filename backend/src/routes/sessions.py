from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.post("/sessions/connect")
def connect_session(request: Request, session_id: str | None = None):
    """
    建立新會話（前端頁面載入時調用）。
    
    Returns:
        sessionId: 新建立的會話 ID
    """
    session_manager = getattr(request.app.state, "session_manager", None)
    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    # 同一分頁重新整理時優先重用既有 session，避免 F5 造成 +1。
    if session_id and session_manager.heartbeat(session_id):
        resolved_session_id = session_id
    else:
        resolved_session_id = session_manager.connect()

    return {
        "sessionId": resolved_session_id,
        "onlineCount": session_manager.get_online_count(),
        "status": "connected",
    }


@router.post("/sessions/heartbeat")
def heartbeat_session(request: Request, session_id: str):
    """
    更新會話心跳（前端定期調用以保持會話活躍）。
    
    Args:
        session_id: 會話 ID
        
    Returns:
        狀態與當前線上人數
    """
    session_manager = getattr(request.app.state, "session_manager", None)
    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    if not session_manager.heartbeat(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "status": "heartbeat_received",
        "onlineCount": session_manager.get_online_count(),
    }


@router.post("/sessions/disconnect")
def disconnect_session(request: Request, session_id: str):
    """
    明確斷開會話（前端頁面卸載時調用）。
    
    Args:
        session_id: 會話 ID
        
    Returns:
        狀態確認
    """
    session_manager = getattr(request.app.state, "session_manager", None)
    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    session_manager.disconnect(session_id)
    return {
        "status": "disconnected",
    }
