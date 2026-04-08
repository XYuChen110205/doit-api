"""统计路由"""
from fastapi import APIRouter, Query
from app.response import success, error
from app.services.stats_service import get_weekly_stats, get_monthly_stats

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("")
async def api_get_stats(
    type: str = Query("week", description="统计类型: week 或 month"),
    date: str = Query(..., description="日期 YYYY-MM-DD")
):
    """S1: 获取统计数据"""
    if type not in ["week", "month"]:
        return error(400, "type 参数必须是 week 或 month")
    
    try:
        if type == "week":
            stats = await get_weekly_stats(date)
        else:
            stats = await get_monthly_stats(date)
        return success(data=stats)
    except Exception as e:
        return error(500, f"获取统计数据失败: {str(e)}")
