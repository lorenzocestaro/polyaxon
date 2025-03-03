# Generated by Django 2.1.7 on 2019-03-07 16:11

from django.db import migrations, models
from django.db.models import Count


def migrate_build_backend(apps, schema_editor):
    BuildJob = apps.get_model('db', 'BuildJob')

    BuildJob.objects.filter(backend__isnull=True).update(backend='native')


def migrate_experiment_backend(apps, schema_editor):
    Experiment = apps.get_model('db', 'Experiment')

    Experiment.objects.filter(backend__isnull=True).update(backend='native')


def migrate_notebook_backend(apps, schema_editor):
    NotebookJob = apps.get_model('db', 'NotebookJob')

    NotebookJob.objects.filter(backend__isnull=True).update(backend='native')


def migrate_build_config(apps, schema_editor):
    BuildJob = apps.get_model('db', 'BuildJob')

    for build in BuildJob.objects.only('config'):
        config = build.config
        config.update(config.pop('build', {}))
        build.config = config
        build.save(update_fields=['config'])


def migrate_distributed_experiments_config(apps, schema_editor):
    Experiment = apps.get_model('db', 'Experiment')

    experiments = Experiment.objects.annotate(
        Count('jobs', distinct=True)).filter(jobs__count__gt=1)
    for xp in experiments:
        config = xp.config
        frameworks = ['tensorflow', 'pytorch', 'horovod', 'mxnet']
        for framework in frameworks:
            if framework in config.get('environment', {}):
                config['framework'] = framework
                config['environment']['replicas'] = config['environment'].pop(framework, {})
        xp.config = config
        xp.save(update_fields=['config'])


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0019_auto_20190221_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='framework',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='experiment',
            name='backend',
            field=models.CharField(blank=True, default='native', max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='experimentjob',
            name='k8s_replica',
            field=models.CharField(default='master', max_length=64),
        ),
        migrations.AddField(
            model_name='notebookjob',
            name='backend',
            field=models.CharField(blank=True, default='notebook', max_length=16, null=True),
        ),
        migrations.RunPython(migrate_build_backend),
        migrations.RunPython(migrate_experiment_backend),
        migrations.RunPython(migrate_notebook_backend),
        migrations.RunPython(migrate_build_config),
        migrations.RunPython(migrate_distributed_experiments_config),
    ]
