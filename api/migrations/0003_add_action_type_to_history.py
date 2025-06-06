from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_loan_loan_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanhistory',
            name='action_type',
            field=models.CharField(
                max_length=10,
                choices=[('LOANED', 'Loaned'), ('RETURNED', 'Returned')],
                default='LOANED'
            ),
        ),
    ]
