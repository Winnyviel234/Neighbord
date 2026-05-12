from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.core.supabase import table
from app.core.cache import cache

class StatisticsRepository:
    def __init__(self):
        self.users_table = table("usuarios")
        self.payments_table = table("pagos")
        self.votings_table = table("votaciones")
        self.votes_table = table("votos")
        self.meetings_table = table("reuniones")
        self.complaints_table = table("solicitudes")
        self.chat_rooms_table = table("chat_rooms")

    def _safe_rows(self, table_name: str, columns: str = "*") -> List[Dict[str, Any]]:
        try:
            rows = table(table_name).select(columns).execute().data or []
            return rows if isinstance(rows, list) else []
        except Exception:
            return []

    def _safe_count(self, table_name: str, query=None) -> int:
        try:
            request = table(table_name).select("id", count="exact")
            if query:
                request = query(request)
            result = request.execute()
            if result.count is not None:
                return result.count
            return len(result.data or [])
        except Exception:
            return 0

    def _count_by_field(self, table_name: str, field: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for row in self._safe_rows(table_name, field):
            value = row.get(field) or "Sin dato"
            counts[str(value)] = counts.get(str(value), 0) + 1
        return counts

    def _recent_count(self, table_name: str, date_field: str, days: int) -> int:
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        for row in self._safe_rows(table_name, date_field):
            value = row.get(date_field)
            if not value:
                continue
            try:
                normalized = str(value).replace("Z", "+00:00")
                parsed = datetime.fromisoformat(normalized)
                if parsed.tzinfo is not None:
                    parsed = parsed.replace(tzinfo=None)
                if parsed >= cutoff:
                    count += 1
            except ValueError:
                continue
        return count

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        # cache_key = "statistics:user_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        return {
            "total_users": self._safe_count("usuarios"),
            "active_users_30d": self._recent_count("usuarios", "created_at", 30),
            "users_by_role": self._count_by_field("usuarios", "rol"),
            "users_by_status": self._count_by_field("usuarios", "estado")
        }

    async def get_payment_statistics(self) -> Dict[str, Any]:
        """Get payment statistics"""
        # cache_key = "statistics:payment_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

        total_count = self._safe_count("pagos")
        amount_result = table("pagos").select("monto").execute()
        total_amount = 0.0
        if amount_result.data:
            for p in amount_result.data:
                try:
                    monto = p.get("monto")
                    if monto is not None:
                        total_amount += float(monto)
                except (ValueError, TypeError):
                    pass  # Skip invalid amounts

        result = {
            "total_payments": total_count,
            "total_amount": total_amount,
            "payments_by_status": self._count_by_field("pagos", "estado"),
            "payments_by_method": self._count_by_field("pagos", "metodo"),
            "recent_payments_30d": self._recent_count("pagos", "created_at", 30)
        }
        # await cache.set(cache_key, result, ttl=180)
        return result

    async def get_voting_statistics(self) -> Dict[str, Any]:
        """Get voting statistics"""
        # cache_key = "statistics:voting_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

        result = {
            "total_votings": self._safe_count("votaciones"),
            "active_votings": self._safe_count("votaciones", lambda q: q.eq("estado", "activa")),
            "total_votes": self._safe_count("votos"),
            "recent_votings_30d": self._recent_count("votaciones", "created_at", 30)
        }
        # await cache.set(cache_key, result, ttl=180)
        return result

    async def get_meeting_statistics(self) -> Dict[str, Any]:
        """Get meeting statistics"""
        # cache_key = "statistics:meeting_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

        now = datetime.now().isoformat()
        total_count = self._safe_count("reuniones")
        upcoming_count = self._safe_count("reuniones", lambda q: q.gte("fecha", now))
        past_count = self._safe_count("reuniones", lambda q: q.lt("fecha", now))

        # Attendance statistics - simplified
        # For now, just set to 0, can be improved later
        total_attendance = 0
        average_attendance = 0

        result = {
            "total_meetings": total_count,
            "upcoming_meetings": upcoming_count,
            "past_meetings": past_count,
            "total_attendance": total_attendance,
            "average_attendance": total_attendance / max(total_count, 1)
        }
        # await cache.set(cache_key, result, ttl=180)
        return result

    async def get_complaint_statistics(self) -> Dict[str, Any]:
        """Get complaint statistics"""
        # cache_key = "statistics:complaint_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

        result = {
            "total_complaints": self._safe_count("solicitudes"),
            "complaints_by_status": self._count_by_field("solicitudes", "estado"),
            "complaints_by_category": self._count_by_field("solicitudes", "categoria"),
            "recent_complaints_30d": self._recent_count("solicitudes", "created_at", 30)
        }
        # await cache.set(cache_key, result, ttl=180)
        return result

    def _get_month_labels(self, months: int = 6) -> list[str]:
        results = []
        now = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year = now.year
        month = now.month
        for _ in range(months):
            results.append(f"{year:04d}-{month:02d}")
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return list(reversed(results))

    def _format_trend_value(self, value: Any) -> float:
        try:
            return float(value) if value is not None else 0.0
        except (TypeError, ValueError):
            return 0.0

    async def get_payment_trends(self, months: int = 6) -> dict:
        """Get payment amount and count trends grouped by month."""
        cache_key = f"statistics:payment_trends:{months}"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        rows = self.payments_table.select("monto,created_at").execute().data or []
        labels = self._get_month_labels(months)
        totals = {label: 0.0 for label in labels}
        counts = {label: 0 for label in labels}

        for row in rows:
            created_at = row.get("created_at")
            if not created_at:
                continue
            try:
                date = datetime.fromisoformat(created_at)
            except ValueError:
                continue
            label = f"{date.year:04d}-{date.month:02d}"
            if label in totals:
                totals[label] += self._format_trend_value(row.get("monto"))
                counts[label] += 1

        result = {
            "months": labels,
            "amounts": [round(totals[label], 2) for label in labels],
            "counts": [counts[label] for label in labels]
        }
        await cache.set(cache_key, result, ttl=180)
        return result

    async def get_complaint_trends(self) -> dict:
        """Get complaint trends by category."""
        cache_key = "statistics:complaint_trends"
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        rows = self.complaints_table.select("categoria,created_at").execute().data or []
        categories: dict[str, int] = {}
        for row in rows:
            category = row.get("categoria") or "Sin categoría"
            categories[category] = categories.get(category, 0) + 1

        result = {
            "categories": categories,
            "total": sum(categories.values())
        }
        await cache.set(cache_key, result, ttl=180)
        return result

    async def get_report_analytics(self) -> Dict[str, Any]:
        """Get a consolidated analytics payload for reports."""
        dashboard = await self.get_dashboard_overview()
        payment_trends = await self.get_payment_trends()
        complaint_trends = await self.get_complaint_trends()

        return {
            "dashboard": dashboard,
            "payment_trends": payment_trends,
            "complaint_trends": complaint_trends
        }

    async def get_chat_statistics(self) -> Dict[str, Any]:
        """Get chat statistics"""
        # Total chat rooms
        try:
            total_rooms = self.chat_rooms_table.select("*", count="exact").execute()
            total_rooms_count = total_rooms.count or 0
        except Exception:
            total_rooms_count = 0

        # Total messages (if messages table exists)
        messages_table = None
        try:
            messages_table = table("messages")
            total_messages = messages_table.select("*", count="exact").execute()
            total_messages_count = total_messages.count or 0
        except Exception:
            total_messages_count = 0

        # Recent activity (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        try:
            if messages_table is None:
                raise RuntimeError("No messages table available")
            recent_messages = messages_table.select("*", count="exact").gte("created_at", seven_days_ago).execute()
            recent_messages_count = recent_messages.count or 0
        except Exception:
            recent_messages_count = 0

        return {
            "total_chat_rooms": total_rooms_count,
            "total_messages": total_messages_count,
            "recent_messages_7d": recent_messages_count
        }

    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get complete dashboard overview"""
        user_stats = await self.get_user_statistics()
        payment_stats = await self.get_payment_statistics()
        voting_stats = await self.get_voting_statistics()
        meeting_stats = await self.get_meeting_statistics()
        complaint_stats = await self.get_complaint_statistics()
        chat_stats = await self.get_chat_statistics()

        return {
            "users": user_stats,
            "payments": payment_stats,
            "votings": voting_stats,
            "meetings": meeting_stats,
            "complaints": complaint_stats,
            "chat": chat_stats,
            "generated_at": datetime.now().isoformat()
        }
