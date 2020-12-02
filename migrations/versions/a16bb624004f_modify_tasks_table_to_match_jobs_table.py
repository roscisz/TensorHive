"""modify tasks table to match jobs table

Revision ID: a16bb624004f
Revises: 4d010fddad6f
Create Date: 2020-11-30 09:19:42.204911

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.automap import automap_base


# revision identifiers, used by Alembic.
revision = 'a16bb624004f'
down_revision = '4d010fddad6f'
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    meta = sa.MetaData()
    meta.reflect(bind=op.get_bind())
    Base = automap_base(metadata=meta)
    Base.prepare()
    Task = Base.classes.tasks

    jobs = sa.Table('jobs', meta)

    new_jobs = []
    tasks = session.query(Task).all()
    for task in tasks:
        new_jobs.append(
            {'name': 'Job from Task {}'.format(str(task.id)),
             'description': 'Job auto-created from task with id: {}'.format(str(task.id)),
             'user_id': task.user_id,
             'status': task.status,
             '_start_at': task.spawn_at,
             '_stop_at': task.terminate_at}
        )

    op.bulk_insert(jobs, new_jobs)

    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }

    with op.batch_alter_table("tasks", naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column('job_id', sa.Integer, nullable=True))
        batch_op.create_foreign_key("fk_tasks_job_id_jobs", 'jobs', ['job_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_constraint("fk_tasks_user_id_users", type_="foreignkey")
        batch_op.drop_column('user_id')
        batch_op.drop_column('spawn_at')
        batch_op.drop_column('terminate_at')

    session.commit()
    session.close()

    session = Session(bind=op.get_bind())
    meta = sa.MetaData()
    meta.reflect(bind=op.get_bind())
    Base = automap_base(metadata=meta)
    Base.prepare()
    Job = Base.classes.jobs

    jobs = session.query(Job).all()
    tasks = sa.Table('tasks', meta)

    for job in jobs:
        if job.name[:-2] == 'Job from Task':
            op.execute(tasks.update()
                .where(tasks.columns.get('id') == job.name[-1]).values(job_id=job.id))

    session.commit()
    session.close()


def downgrade():
    session = Session(bind=op.get_bind())
    meta = sa.MetaData()
    meta.reflect(bind=op.get_bind())

    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }

    with op.batch_alter_table("tasks", naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer, nullable=True))
        batch_op.create_foreign_key('fk_tasks_user_id_users', 'users', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.add_column(sa.Column('spawn_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('terminate_at', sa.DateTime(), nullable=True))

    session.commit()
    session.close()

    session = Session(bind=op.get_bind())
    meta = sa.MetaData()
    meta.reflect(bind=op.get_bind())
    Base = automap_base(metadata=meta)
    Base.prepare()
    Task = Base.classes.tasks
    Job = Base.classes.jobs

    tasks_table = sa.Table('tasks', meta)
    jobs_table = sa.Table('jobs', meta)
    tasks = session.query(Task).all()
    jobs = session.query(Job).all()

    for task in tasks:
        job = session.query(Job).filter_by(id=task.job_id).one()
        op.execute(tasks_table.update()
            .where(tasks_table.columns.get('id') == task.id).values({
                'user_id': job.user_id,
                'spawn_at': job._start_at,
                'terminate_at': job._stop_at,
            })
        )

    session.query(Job).delete()

    with op.batch_alter_table("tasks", naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint("fk_tasks_job_id_jobs", type_="foreignkey")
        batch_op.drop_column('job_id')

    session.commit()
    session.close()
