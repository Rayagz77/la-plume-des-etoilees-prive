"""Initial migration

Revision ID: 21f30ce6f9a1
Revises: 
Create Date: 2024-11-24 19:39:11.272600

"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '21f30ce6f9a1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Création de la table 'orders' si elle n'existe pas déjà
    if not op.get_bind().dialect.has_table(op.get_bind(), "orders"):
        op.create_table(
            'orders',
            sa.Column('order_id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('order_date', sa.DateTime(), nullable=False),
            sa.Column('total_price', sa.Float(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['User.user_id']),
        )

    # Modification de la table 'Category'
    op.create_unique_constraint('uq_category_name', 'Category', ['category_name'])

    # Modification de la table 'order_details'
    with op.batch_alter_table('order_details', schema=None) as batch_op:
        # Ajout de la colonne si elle n'existe pas déjà
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        columns = [col['name'] for col in inspector.get_columns('order_details')]
        if 'order_details_id' not in columns:
            batch_op.add_column(sa.Column('order_details_id', sa.Integer(), autoincrement=True, nullable=True))

        # Assigner des valeurs uniques à la colonne si nécessaire
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='order_details' AND column_name='order_details_id') THEN
                    UPDATE order_details SET order_details_id = nextval('order_details_id_seq') WHERE order_details_id IS NULL;
                END IF;
            END $$;
        """)

        # Vérification et nettoyage des données invalides
        op.execute("""
            DELETE FROM order_details WHERE order_id NOT IN (SELECT order_id FROM orders);
        """)

        # Rendre la colonne obligatoire
        batch_op.alter_column('order_details_id', nullable=False)

        # Ajout de la contrainte de clé étrangère
        batch_op.create_foreign_key('fk_order_id', 'orders', ['order_id'], ['order_id'])


def downgrade():
    # Revenir aux modifications précédentes
    with op.batch_alter_table('order_details', schema=None) as batch_op:
        if batch_op.dialect.has_constraint(batch_op.bind, 'fk_order_id'):
            batch_op.drop_constraint('fk_order_id', type_='foreignkey')

        if batch_op.dialect.has_column(batch_op.bind, 'order_details_id'):
            batch_op.drop_column('order_details_id')

        batch_op.alter_column(
            'unit_price',
            existing_type=sa.Float(),
            type_=sa.NUMERIC(precision=10, scale=2),
            existing_nullable=False
        )

    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.alter_column(
            'user_signup_date',
            existing_type=sa.DateTime(),
            type_=sa.DATE(),
            nullable=True
        )
        batch_op.alter_column(
            'user_email',
            existing_type=sa.String(length=100),
            type_=sa.VARCHAR(length=255),
            existing_nullable=False
        )
        batch_op.alter_column(
            'user_lastname',
            existing_type=sa.String(length=50),
            type_=sa.VARCHAR(length=100),
            existing_nullable=False
        )
        batch_op.alter_column(
            'user_firstname',
            existing_type=sa.String(length=50),
            type_=sa.VARCHAR(length=100),
            existing_nullable=False
        )

    op.drop_constraint('uq_category_name', 'Category', type_='unique')

    # Suppression de la table 'orders' est désactivée
    # op.drop_table('orders')
