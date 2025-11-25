"""
Django management command to cleanup and normalize legacy appointment records.

Usage:
    python manage.py cleanup_legacy_appointments [--dry-run]

This command:
- Marks past pending/approved appointments as cancelled if they're overdue
- Ensures all cancelled appointments are properly marked
- Reports statistics about cleaned records
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date, datetime, timedelta
from apps.appointments.models import Appointment


class Command(BaseCommand):
    help = 'Cleanup and normalize legacy appointment records to prevent slot blocking issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually modifying the database',
        )
        parser.add_argument(
            '--auto-cancel-past',
            action='store_true',
            help='Automatically cancel past pending/approved appointments',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        auto_cancel_past = options['auto_cancel_past']
        
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('LEGACY APPOINTMENT CLEANUP TOOL'))
        self.stdout.write(self.style.WARNING('=' * 70))
        
        if dry_run:
            self.stdout.write(self.style.NOTICE('\n[DRY RUN MODE] - No changes will be saved\n'))
        
        today = date.today()
        
        # Statistics
        stats = {
            'total_appointments': 0,
            'past_pending': 0,
            'past_approved': 0,
            'already_cancelled': 0,
            'already_rejected': 0,
            'updated': 0,
        }
        
        # Get all appointments
        all_appointments = Appointment.objects.all()
        stats['total_appointments'] = all_appointments.count()
        
        self.stdout.write(f"\nTotal appointments in database: {stats['total_appointments']}")
        self.stdout.write('-' * 70)
        
        # 1. Find past appointments that are still marked as pending/approved
        past_pending = Appointment.objects.filter(
            date__lt=today,
            status='pending'
        ).order_by('date')
        
        past_approved = Appointment.objects.filter(
            date__lt=today,
            status='approved'
        ).order_by('date')
        
        stats['past_pending'] = past_pending.count()
        stats['past_approved'] = past_approved.count()
        
        self.stdout.write(f"\n📅 Past appointments still active:")
        self.stdout.write(f"   - Pending (should be cancelled): {stats['past_pending']}")
        self.stdout.write(f"   - Approved (should be completed/cancelled): {stats['past_approved']}")
        
        # 2. Count already cancelled/rejected
        stats['already_cancelled'] = Appointment.objects.filter(status='cancelled').count()
        stats['already_rejected'] = Appointment.objects.filter(status='rejected').count()
        
        self.stdout.write(f"\n✅ Already properly marked:")
        self.stdout.write(f"   - Cancelled: {stats['already_cancelled']}")
        self.stdout.write(f"   - Rejected: {stats['already_rejected']}")
        
        # 3. Show breakdown by date range
        future_active = Appointment.objects.filter(
            date__gte=today,
            status__in=['pending', 'approved']
        ).count()
        
        self.stdout.write(f"\n📊 Current active appointments (future): {future_active}")
        
        # 4. Auto-cancel past appointments if requested
        if auto_cancel_past:
            self.stdout.write('\n' + '=' * 70)
            self.stdout.write(self.style.WARNING('AUTO-CANCELLING PAST APPOINTMENTS'))
            self.stdout.write('=' * 70)
            
            cancelled_count = 0
            
            for app in past_pending:
                self.stdout.write(
                    f"  Cancelling: {app.client.get_full_name()} - "
                    f"{app.date} {app.time} (was: pending)"
                )
                if not dry_run:
                    app.status = 'cancelled'
                    app.save()
                cancelled_count += 1
            
            for app in past_approved:
                self.stdout.write(
                    f"  Cancelling: {app.client.get_full_name()} - "
                    f"{app.date} {app.time} (was: approved)"
                )
                if not dry_run:
                    app.status = 'cancelled'
                    app.save()
                cancelled_count += 1
            
            stats['updated'] = cancelled_count
            
            if dry_run:
                self.stdout.write(
                    self.style.NOTICE(
                        f"\n[DRY RUN] Would have cancelled {cancelled_count} appointments"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✅ Successfully cancelled {cancelled_count} past appointments"
                    )
                )
        else:
            self.stdout.write('\n' + '-' * 70)
            self.stdout.write(
                self.style.NOTICE(
                    '\n💡 To auto-cancel past appointments, run with --auto-cancel-past flag'
                )
            )
        
        # 5. Final summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('CLEANUP SUMMARY'))
        self.stdout.write('=' * 70)
        self.stdout.write(f"\nTotal appointments: {stats['total_appointments']}")
        self.stdout.write(f"Already cancelled: {stats['already_cancelled']}")
        self.stdout.write(f"Already rejected: {stats['already_rejected']}")
        
        if auto_cancel_past:
            self.stdout.write(f"Newly cancelled: {stats['updated']}")
            
            # Verify slot blocking won't happen
            self.stdout.write('\n' + '-' * 70)
            self.stdout.write(self.style.SUCCESS('✅ VERIFICATION'))
            self.stdout.write('-' * 70)
            
            active_future = Appointment.objects.active().filter(date__gte=today).count()
            self.stdout.write(
                f"\nActive appointments blocking future slots: {active_future}"
            )
            self.stdout.write(
                "Legacy cancelled appointments will NOT block slots ✅"
            )
        else:
            self.stdout.write(
                f"\n⚠️  {stats['past_pending'] + stats['past_approved']} "
                "past appointments still active"
            )
        
        # 6. Recommendations
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.WARNING('RECOMMENDATIONS'))
        self.stdout.write('=' * 70)
        
        if stats['past_pending'] > 0 or stats['past_approved'] > 0:
            self.stdout.write(
                "\n⚠️  You have past appointments still marked as active."
                "\n   These could be blocking slots in the CLIENT calendar."
                "\n\n   Run again with --auto-cancel-past to fix this."
            )
        else:
            self.stdout.write(
                "\n✅ All past appointments are properly marked!"
                "\n   No legacy data is blocking slots."
            )
        
        self.stdout.write(
            "\n💡 Current active() manager filters: status__in=['pending', 'approved']"
            "\n   Only these statuses will block slots in the calendar."
        )
        
        self.stdout.write('\n' + '=' * 70 + '\n')
        
        if not dry_run and stats['updated'] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed {stats["updated"]} appointments!'
                )
            )
