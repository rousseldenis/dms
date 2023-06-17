# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def convert_root_storage_id_in_storage_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE dms_directory
        SET storage_id = root_storage_id
        WHERE root_storage_id IS NOT NULL
        AND parent_id IS NULL
        """,
    )


def _delete_dms_views(env):
    for model, table in (("ir.ui.view", "ir_ui_view"),):
        openupgrade.logged_query(
            env.cr,
            f"""
                delete from {table}
                where id in (
                    select res_id from ir_model_data imd
                    left join ir_module_module imm on imm.name=imd.module
                    where (imm.name = 'dms') and model='{model}'
                )
                """,
        )
        openupgrade.logged_query(
            env.cr,
            f"""
                delete from ir_model_data
                where model='{model}'
                and module in (
                    select name from ir_module_module where (name = 'dms')
                )
                """,
        )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
            SET state = 'to update'
            WHERE name = 'dms'
    """,
    )


@openupgrade.migrate()
def migrate(env, version):
    convert_root_storage_id_in_storage_id(env)
    _delete_dms_views(env)
