from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WhatsAppUser",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone_number", models.CharField(max_length=32, unique=True)),
                ("locale", models.CharField(default="en", max_length=16)),
                ("timezone", models.CharField(default="UTC", max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64)),
                ("type", models.CharField(choices=[("bank", "Bank"), ("cash", "Cash")], max_length=16)),
                ("balance", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tracker.whatsappuser")),
            ],
            options={
                "unique_together": {("user", "name", "type")},
            },
        ),
        migrations.CreateModel(
            name="Card",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("issuer", models.CharField(max_length=64)),
                ("last4", models.CharField(blank=True, max_length=4)),
                ("billing_cycle_day", models.PositiveSmallIntegerField(default=1)),
                ("credit_limit", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tracker.whatsappuser")),
            ],
            options={
                "unique_together": {("user", "issuer", "last4")},
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64)),
                ("aliases", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tracker.whatsappuser")),
            ],
            options={
                "unique_together": {("user", "name")},
            },
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="inr", max_length=8)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("source_type", models.CharField(choices=[("card", "Card"), ("account", "Account"), ("cash", "Cash")], max_length=16)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="tracker.category")),
                ("source_account", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="tracker.account")),
                ("source_card", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="tracker.card")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tracker.whatsappuser")),
            ],
            options={
                "indexes": [
                    models.Index(fields=["user", "date"], name="tracker_expense_user_id_date_idx"),
                    models.Index(fields=["user", "category"], name="tracker_expense_user_id_category_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("raw_text", models.TextField()),
                ("parsed_intent", models.CharField(blank=True, max_length=64)),
                ("status", models.CharField(choices=[("received", "Received"), ("processed", "Processed"), ("rejected", "Rejected")], default="received", max_length=32)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tracker.whatsappuser")),
            ],
            options={
                "indexes": [
                    models.Index(fields=["idempotency_key"], name="tracker_message_idempotency_key_idx"),
                ],
            },
        ),
    ]
