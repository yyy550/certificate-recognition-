"""
管理员面板模块
实现管理员的用户管理、数据查看、导出等功能
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from database import db_manager
from data_export import DataExporter
from user_import import UserImportManager
import pandas as pd
from datetime import datetime, timedelta


class AdminPanel:
    """管理员面板"""

    def __init__(self):
        self.db = db_manager
        self.exporter = DataExporter()
        self.user_importer = UserImportManager()

    def show_admin_dashboard(self):
        """显示管理员仪表板"""
        st.header("🏠 管理员仪表板")

        # 获取统计数据
        stats = self.db.get_statistics()

        # 显示关键指标
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("总用户数", stats.get("total_users", 0))

        with col2:
            st.metric("学生用户", stats.get("student_count", 0))

        with col3:
            st.metric("教师用户", stats.get("teacher_count", 0))

        with col4:
            st.metric("证书记录", stats.get("total_certificates", 0))

        # 显示最近活动
        st.subheader("📊 近期统计")

        # 这里可以添加图表显示
        # 暂时显示文字统计
        submitted_count = stats.get("submitted_certificates", 0)
        draft_count = stats.get("total_certificates", 0) - submitted_count

        col5, col6 = st.columns(2)

        with col5:
            st.info(f"已提交证书：{submitted_count}")

        with col6:
            st.info(f"草稿证书：{draft_count}")

    def show_user_management(self):
        """显示用户管理界面"""
        st.header("👥 用户管理")

        # 用户列表显示
        st.subheader("用户列表")

        # 筛选条件
        col1, col2 = st.columns(2)

        with col1:
            role_filter = st.selectbox(
                "角色筛选",
                ["全部", "学生", "教师", "管理员"],
                help="按用户角色筛选"
            )

        with col2:
            status_filter = st.selectbox(
                "状态筛选",
                ["全部", "启用", "禁用"],
                help="按账号状态筛选"
            )

        # 获取用户列表
        try:
            if role_filter == "全部":
                users = self.db.get_all_users()
            else:
                role_map = {"学生": "student", "教师": "teacher", "管理员": "admin"}
                role_key = role_map.get(role_filter, "")
                users = self.db.get_all_users(role_key) if role_key else self.db.get_all_users()

            # 状态筛选
            if status_filter != "全部":
                status_map = {"启用": True, "禁用": False}
                is_active = status_map.get(status_filter)
                users = [u for u in users if u.is_active == is_active]

            if users:
                # 显示用户表格
                user_data = []
                for user in users:
                    user_data.append({
                        "用户ID": user.user_id,
                        "学(工)号": user.account_id,
                        "姓名": user.name,
                        "角色": "学生" if user.role == "student" else "教师" if user.role == "teacher" else "管理员",
                        "单位": user.department,
                        "邮箱": user.email,
                        "状态": "启用" if user.is_active else "禁用",
                        "注册时间": user.created_at.strftime("%Y-%m-%d %H:%M")
                    })

                df = pd.DataFrame(user_data)
                st.dataframe(df, use_container_width=True)

                # 用户操作
                st.subheader("用户操作")

                # 选择用户进行操作
                selected_user = st.selectbox(
                    "选择用户",
                    [f"{u.account_id} - {u.name}" for u in users],
                    help="选择要操作的用户"
                )

                if selected_user:
                    selected_account_id = selected_user.split(" - ")[0]
                    selected_user_obj = next((u for u in users if u.account_id == selected_account_id), None)

                    if selected_user_obj:
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            if st.button("重置密码", use_container_width=True):
                                # 这里可以实现密码重置功能
                                st.info("密码重置功能开发中...")

                        with col2:
                            new_status = not selected_user_obj.is_active
                            status_text = "启用账号" if not selected_user_obj.is_active else "禁用账号"
                            if st.button(status_text, use_container_width=True):
                                success = self.db.update_user(selected_user_obj.user_id, {"is_active": new_status})
                                if success:
                                    st.success(f"账号已{'启用' if new_status else '禁用'}")
                                    st.rerun()
                                else:
                                    st.error("操作失败")

                        with col3:
                            if st.button("编辑信息", use_container_width=True):
                                # 这里可以实现用户信息编辑功能
                                st.info("编辑功能开发中...")

            else:
                st.info("暂无用户数据")

        except Exception as e:
            st.error(f"加载用户数据失败：{str(e)}")

        # 批量导入用户
        st.markdown("---")
        st.subheader("批量导入用户")

        # 这里可以调用user_import模块的功能
        if st.button("📤 进入用户导入", use_container_width=True):
            st.session_state.admin_page = "user_import"
            st.rerun()

    def show_data_view(self):
        """显示数据查看界面"""
        st.header("📊 数据查看")

        # 筛选条件
        col1, col2, col3 = st.columns(3)

        with col1:
            submitter_role = st.selectbox(
                "提交者角色",
                ["全部", "学生", "教师"]
            )

        with col2:
            department = st.selectbox(
                "学院",
                ["全部"]  # 这里可以动态获取学院列表
            )

        with col3:
            award_level = st.selectbox(
                "获奖等级",
                ["全部", "一等奖", "二等奖", "三等奖", "金奖", "银奖", "铜奖", "优秀奖"]
            )

        # 构建筛选条件
        filters = {}
        if submitter_role != "全部":
            filters["submitter_role"] = submitter_role.lower()
        if award_level != "全部":
            filters["award_level"] = award_level

        # 获取数据
        try:
            certificates = self.db.get_all_certificates(filters)

            if certificates:
                st.success(f"找到 {len(certificates)} 条记录")

                # 显示数据表格
                cert_data = []
                for cert in certificates:
                    cert_data.append({
                        "提交者角色": "学生" if cert.submitter_role == "student" else "教师",
                        "学生学号": cert.student_id,
                        "学生姓名": cert.student_name,
                        "学院": cert.department,
                        "竞赛项目": cert.competition_name,
                        "获奖等级": cert.award_level,
                        "获奖类别": cert.award_category,
                        "竞赛类型": cert.competition_type,
                        "主办单位": cert.organizer,
                        "获奖时间": cert.award_date,
                        "指导教师": cert.advisor,
                        "状态": "已提交" if cert.status == "submitted" else "草稿",
                        "提交时间": cert.created_at.strftime("%Y-%m-%d %H:%M")
                    })

                df = pd.DataFrame(cert_data)
                st.dataframe(df, use_container_width=True)

                # 数据分析
                st.subheader("📈 数据分析")

                # 获奖等级分布
                level_counts = df["获奖等级"].value_counts()
                st.bar_chart(level_counts)

                # 学院分布
                dept_counts = df["学院"].value_counts()
                st.bar_chart(dept_counts)

            else:
                st.info("没有找到符合条件的记录")

        except Exception as e:
            st.error(f"加载数据失败：{str(e)}")

    def show_data_export(self):
        """显示数据导出界面"""
        st.header("📤 数据导出")

        # 这里可以调用data_export模块的功能
        from data_export import show_export_ui
        show_export_ui()

    def show_system_config(self):
        """显示系统配置界面"""
        st.header("⚙️ 系统配置")

        st.subheader("截止时间设置")

        # 获取当前截止时间
        deadline_config = self.db.get_config("deadline")
        current_deadline = deadline_config.config_value if deadline_config else ""

        # 截止时间设置
        col1, col2 = st.columns(2)

        with col1:
            new_deadline = st.date_input(
                "设置证书提交截止时间",
                value=datetime.now().date() + timedelta(days=30) if not current_deadline else datetime.strptime(current_deadline, "%Y-%m-%d").date(),
                help="设置后用户将无法提交新证书"
            )

        with col2:
            if st.button("保存截止时间", use_container_width=True):
                deadline_str = new_deadline.strftime("%Y-%m-%d")
                success = self.db.set_config("deadline", deadline_str, "证书提交截止时间", st.session_state.user["user_id"])
                if success:
                    st.success(f"截止时间已设置为：{deadline_str}")
                else:
                    st.error("保存失败")

        if current_deadline:
            st.info(f"当前截止时间：{current_deadline}")

        # 其他配置项
        st.subheader("API配置")

        # 默认API设置
        default_api_config = self.db.get_config("default_api")
        current_api = default_api_config.config_value if default_api_config else "glm4v"

        new_api = st.selectbox(
            "默认识别API",
            ["glm4v", "baidu", "aliyun", "tencent", "local"],
            index=["glm4v", "baidu", "aliyun", "tencent", "local"].index(current_api),
            help="设置默认的证书信息识别API"
        )

        if st.button("保存API设置", use_container_width=True):
            success = self.db.set_config("default_api", new_api, "默认识别API", st.session_state.user["user_id"])
            if success:
                st.success(f"默认API已设置为：{new_api}")
            else:
                st.error("保存失败")

    def show_user_import(self):
        """显示用户导入界面"""
        st.header("👥 用户批量导入")

        # 这里可以调用user_import模块的功能
        from user_import import show_import_ui
        show_import_ui()

        # 返回按钮
        if st.button("← 返回用户管理", use_container_width=True):
            st.session_state.admin_page = "user_management"
            st.rerun()


def show_admin_panel():
    """显示管理员面板主界面"""
    # 检查管理员权限
    user = st.session_state.get("user", {})
    if user.get("role") != "admin":
        st.error("需要管理员权限")
        return

    # 初始化管理员面板
    admin_panel = AdminPanel()

    # 获取当前子页面，如果没有则默认为仪表板
    if "admin_page" not in st.session_state:
        st.session_state.admin_page = "dashboard"
    
    # 根据auth_system中的导航设置当前子页面
    current_page = st.session_state.get("current_page", "dashboard")
    if current_page == "dashboard":
        st.session_state.admin_page = "dashboard"
    elif current_page == "user_management":
        st.session_state.admin_page = "user_management"
    elif current_page == "data_view":
        st.session_state.admin_page = "data_view"
    elif current_page == "data_export":
        st.session_state.admin_page = "data_export"
    elif current_page == "system_config":
        st.session_state.admin_page = "system_config"

    # 根据导航项显示对应内容
    current_admin_page = st.session_state.admin_page
    if current_admin_page == "dashboard":
        admin_panel.show_admin_dashboard()
    elif current_admin_page == "user_management":
        admin_panel.show_user_management()
    elif current_admin_page == "data_view":
        admin_panel.show_data_view()
    elif current_admin_page == "data_export":
        admin_panel.show_data_export()
    elif current_admin_page == "system_config":
        admin_panel.show_system_config()
    elif current_admin_page == "user_import":
        admin_panel.show_user_import()


def main():
    """主函数 - 用于测试"""
    st.title("管理员面板测试")

    # 模拟管理员登录
    if "user" not in st.session_state:
        st.session_state.user = {
            "user_id": 1,
            "account_id": "admin",
            "name": "管理员",
            "role": "admin",
            "department": "管理员"
        }

    show_admin_panel()


if __name__ == "__main__":
    main()
