from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.get("/stats/online_users")
def get_online_users(request: Request):
    """
    取得當前線上使用者數量。
    
    Returns:
        onlineCount: 當前線上使用者數
    """
    session_manager = getattr(request.app.state, "session_manager", None)
    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    return {
        "onlineCount": session_manager.get_online_count(),
    }
