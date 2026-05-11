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

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        # cache_key = "statistics:user_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Total users
            total_users = self.users_table.select("*", count="exact").execute()
            total_count = total_users.count or 0

            # Active users (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            active_users = self.users_table.select("*", count="exact").gte("created_at", thirty_days_ago).execute()
            active_count = active_users.count or 0

            # Users by role
            role_stats = self.users_table.select("rol", count="exact").execute()
            roles = {}
            for stat in role_stats.data or []:
                roles[stat["rol"]] = stat["count"]

            # Users by status
            status_stats = self.users_table.select("estado", count="exact").execute()
            statuses = {}
            for stat in status_stats.data or []:
                statuses[stat["estado"]] = stat["count"]

            result = {
                "total_users": total_count,
                "active_users_30d": active_count,
                "users_by_role": roles,
                "users_by_status": statuses
            }
            return result
        except Exception as e:
            return {
                "total_users": 0,
                "active_users_30d": 0,
                "users_by_role": {},
                "users_by_status": {}
            }

    async def get_payment_statistics(self) -> Dict[str, Any]:
        """Get payment statistics"""
        # cache_key = "statistics:payment_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

        # Total payments
        total_payments = self.payments_table.select("*", count="exact").execute()
        total_count = total_payments.count or 0

        # Total amount
        amount_result = self.payments_table.select("monto").execute()
        total_amount = 0.0
        if amount_result.data:
            for p in amount_result.data:
                try:
                    monto = p.get("monto")
                    if monto is not None:
                        total_amount += float(monto)
                except (ValueError, TypeError):
                    pass  # Skip invalid amounts

        # Payments by status
        status_stats = self.payments_table.select("estado", count="exact").execute()
        statuses = {}
        for stat in status_stats.data or []:
            statuses[stat["estado"]] = stat["count"]

        # Payments by method
        method_stats = self.payments_table.select("metodo", count="exact").execute()
        methods = {}
        for stat in method_stats.data or []:
            methods[stat["metodo"]] = stat["count"]

        # Recent payments (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_payments = self.payments_table.select("*", count="exact").gte("created_at", thirty_days_ago).execute()
        recent_count = recent_payments.count or 0

        result = {
            "total_payments": total_count,
            "total_amount": total_amount,
            "payments_by_status": statuses,
            "payments_by_method": methods,
            "recent_payments_30d": recent_count
        }
        # await cache.set(cache_key, result, ttl=180)
        return result

    async def get_voting_statistics(self) -> Dict[str, Any]:
        """Get voting statistics"""
        # cache_key = "statistics:voting_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

        # Total votings
        total_votings = self.votings_table.select("*", count="exact").execute()
        total_count = total_votings.count or 0

        # Active votings
        active_votings = self.votings_table.select("*", count="exact").eq("estado", "activa").execute()
        active_count = active_votings.count or 0

        # Total votes
        total_votes = self.votes_table.select("*", count="exact").execute()
        votes_count = total_votes.count or 0

        # Recent votings (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_votings = self.votings_table.select("*", count="exact").gte("created_at", thirty_days_ago).execute()
        recent_count = recent_votings.count or 0

        result = {
            "total_votings": total_count,
            "active_votings": active_count,
            "total_votes": votes_count,
            "recent_votings_30d": recent_count
        }
        # await cache.set(cache_key, result, ttl=180)
        return result

    async def get_meeting_statistics(self) -> Dict[str, Any]:
        """Get meeting statistics"""
        # cache_key = "statistics:meeting_statistics"
        # cached = await cache.get(cache_key)
        # if cached is not None:
        #     return cached

        # Total meetings
        total_meetings = self.meetings_table.select("*", count="exact").execute()
        total_count = total_meetings.count or 0

        # Upcoming meetings
        now = datetime.now().isoformat()
        upcoming_meetings = self.meetings_table.select("*", count="exact").gte("fecha", now).execute()
        upcoming_count = upcoming_meetings.count or 0

        # Past meetings
        past_meetings = self.meetings_table.select("*", count="exact").lt("fecha", now).execute()
        past_count = past_meetings.count or 0

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

        # Total complaints
        total_complaints = self.complaints_table.select("*", count="exact").execute()
        total_count = total_complaints.count or 0

        # Complaints by status
        status_stats = self.complaints_table.select("estado", count="exact").execute()
        statuses = {}
        for stat in status_stats.data or []:
            statuses[stat["estado"]] = stat["count"]

        # Complaints by category
        category_stats = self.complaints_table.select("categoria", count="exact").execute()
        categories = {}
        for stat in category_stats.data or []:
            categories[stat["categoria"]] = stat["count"]

        # Recent complaints (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_complaints = self.complaints_table.select("*", count="exact").gte("created_at", thirty_days_ago).execute()
        recent_count = recent_complaints.count or 0

        result = {
            "total_complaints": total_count,
            "complaints_by_status": statuses,
            "complaints_by_category": categories,
            "recent_complaints_30d": recent_count
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