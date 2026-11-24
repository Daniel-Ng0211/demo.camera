

import streamlit as st
import pandas as pd

from database import (
    init_db,
    add_customer,
    list_customers,
    update_customer,
    delete_customer,
    check_in,
    check_out,
    active_visits,
    visit_history,
    get_stats,
    daily_visit_stats
)

from agent import CustomerAgent


# ======================================
# 1. CAU HINH UNG DUNG
# ======================================

st.set_page_config(
    page_title="AI Customer Agent",
    page_icon="📷",
    layout="wide"
)

init_db()

agent = CustomerAgent()

st.title("📷 AI CUSTOMER AGENT")
st.caption("Hệ thống quản lý khách hàng và lịch sử ra vào")


# ======================================
# 2. MENU DIEU HUONG
# ======================================

st.sidebar.title("QUẢN LÝ HỆ THỐNG")

page = st.sidebar.radio(
    "Chọn chức năng",
    [
        "Dashboard",
        "Quản lý khách hàng",
        "Khách vào phòng",
        "Khách ra phòng",
        "Lịch sử ra vào",
        "AI Agent"
    ]
)


# ======================================
# 3. DASHBOARD
# ======================================

if page == "Dashboard":

    st.header("Tổng quan hệ thống")

    stats = get_stats()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Tổng khách hàng",
        stats["total_customers"]
    )

    col2.metric(
        "Lượt vào hôm nay",
        stats["today_visits"]
    )

    col3.metric(
        "Khách đang trong phòng",
        stats["current_visitors"]
    )
  
    st.divider()

    st.subheader("📊 Thống kê lượt khách trong 7 ngày")

    chart_data = daily_visit_stats(7)

    if chart_data:

        df = pd.DataFrame(chart_data)

        st.bar_chart(
            df,
            x="visit_date",
            y="total_visits"
        )

    else:

        st.info(
            "Chưa có dữ liệu thống kê."
        )


    if history:
        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )

# ======================================
# QUAN LY KHACH HANG - CRUD
# ======================================



elif page == "Quản lý khách hàng":

    st.header("👥 QUẢN LÝ KHÁCH HÀNG")

    # =================================
    # CREATE - THEM KHACH HANG
    # =================================

    st.subheader("➕ Thêm khách hàng")

    with st.form("add_customer_form"):

        code = st.text_input(
            "Mã khách hàng",
            placeholder="KH001"
        )

        name = st.text_input(
            "Họ và tên",
            placeholder="Nguyễn Văn A"
        )

        submitted = st.form_submit_button(
            "THÊM KHÁCH HÀNG"
        )

        if submitted:

            try:

                add_customer(code, name)

                st.success(
                    "Thêm khách hàng thành công!"
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))

    st.divider()

    # =================================
    # READ - TIM KIEM
    # =================================

    st.subheader("🔍 Danh sách khách hàng")

    keyword = st.text_input(
        "Tìm kiếm theo mã hoặc họ tên"
    )

    customers = list_customers(keyword)

    if customers:

        st.dataframe(
            customers,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Không tìm thấy khách hàng.")

    st.divider()

    # =================================
    # UPDATE - SUA THONG TIN
    # =================================

    st.subheader("✏️ Chỉnh sửa khách hàng")

    all_customers = list_customers()

    if all_customers:

        customer_map = {
            item["id"]: (
                item["customer_code"]
                + " - "
                + item["full_name"]
            )
            for item in all_customers
        }

        selected_id = st.selectbox(
            "Chọn khách hàng cần sửa",
            options=list(customer_map.keys()),
            format_func=lambda x: customer_map[x],
            key="edit_customer_select"
        )

        selected = next(
            item for item in all_customers
            if item["id"] == selected_id
        )

        with st.form("edit_customer_form"):

            new_code = st.text_input(
                "Mã khách hàng",
                value=selected["customer_code"]
            )

            new_name = st.text_input(
                "Họ và tên",
                value=selected["full_name"]
            )

            submitted = st.form_submit_button(
                "LƯU THAY ĐỔI"
            )

            if submitted:

                try:

                    update_customer(
                        selected_id,
                        new_code,
                        new_name
                    )

                    st.success(
                        "Cập nhật thành công!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

        st.divider()

        # =================================
        # DELETE - XOA KHACH HANG
        # =================================

        st.subheader("🗑️ Xóa khách hàng")

        confirm = st.checkbox(
            "Tôi xác nhận muốn xóa hồ sơ khách hàng đã chọn."
        )

        if st.button(
            "XÓA KHÁCH HÀNG",
            type="secondary"
        ):

            if not confirm:

                st.warning(
                    "Vui lòng xác nhận trước khi xóa."
                )

            else:

                try:

                    delete_customer(selected_id)

                    st.success(
                        "Xóa khách hàng thành công!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

    else:

        st.info("Chưa có khách hàng để chỉnh sửa.")

    st.divider()

    # ----------------------------------
    # 4. XOA KHACH HANG
    # ----------------------------------

    st.subheader("🗑️ Xóa khách hàng")

    if all_customers:

        delete_id = st.selectbox(
            "Chọn khách hàng cần xóa",
            options=list(customer_map.keys()),
            format_func=lambda x: customer_map[x],
            key="delete_customer_id"
        )

        confirm_delete = st.checkbox(
            "Tôi xác nhận muốn xóa hồ sơ này."
        )

        if st.button(
            "XÓA KHÁCH HÀNG",
            type="secondary"
        ):

            if not confirm_delete:

                st.warning(
                    "Bạn cần xác nhận trước khi xóa."
                )

            else:

                try:

                    delete_customer(delete_id)

                    st.success(
                        "Đã xóa khách hàng thành công!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

    else:

        st.info("Không có hồ sơ để xóa.")

# ======================================
# 5. KHACH VAO PHONG
# ======================================

elif page == "Khách vào phòng":

    st.header("Ghi nhận khách vào phòng")

    st.info(
        "Ảnh webcam chỉ được sử dụng để xác nhận "
        "trong phiên làm việc này, không được lưu "
        "vào database."
    )

    photo = st.camera_input(
        "Chụp ảnh khách hàng bằng webcam"
    )

    if photo is not None:

        st.image(
            photo,
            caption="Ảnh vừa chụp",
            width=300
        )

    st.divider()

    customers = list_customers()

    if not customers:

        st.warning(
            "Bạn cần thêm khách hàng trước."
        )

    else:

        customer_map = {
            item["id"]: (
                item["customer_code"]
                + " - "
                + item["full_name"]
            )
            for item in customers
        }

        verified = st.checkbox(
            "Tôi đã xác minh danh tính khách trực tiếp "
            "(không sử dụng ảnh webcam)."
        )

        with st.form("checkin_form"):

            customer_id = st.selectbox(
                "Chọn khách hàng",
                options=list(customer_map.keys()),
                format_func=lambda x: customer_map[x]
            )

            purpose = st.text_input(
                "Mục đích đến"
            )

            submitted = st.form_submit_button(
                "XÁC NHẬN KHÁCH VÀO"
            )

            if submitted:

                if photo is None and not verified:

                    st.warning(
                        "Hãy chụp ảnh webcam hoặc "
                        "xác minh trực tiếp trước khi tiếp tục."
                    )

                else:

                    try:

                        check_in(
                            customer_id,
                            purpose
                        )

                        st.success(
                            "Đã ghi nhận khách vào phòng!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))


# ======================================
# 6. KHACH RA PHONG
# ======================================

elif page == "Khách ra phòng":

    st.header("Ghi nhận khách ra phòng")

    visitors = active_visits()

    if not visitors:

        st.info(
            "Hiện không có khách đang ở trong phòng."
        )

    else:

        visit_map = {
            item["visit_id"]: (
                item["customer_code"]
                + " - "
                + item["full_name"]
            )
            for item in visitors
        }

        with st.form("checkout_form"):

            visit_id = st.selectbox(
                "Chọn khách hàng",
                options=list(visit_map.keys()),
                format_func=lambda x: visit_map[x]
            )

            submitted = st.form_submit_button(
                "XÁC NHẬN KHÁCH RA"
            )

            if submitted:

                try:

                    check_out(visit_id)

                    st.success(
                        "Đã ghi nhận khách ra phòng!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))


# ======================================
# 7. LICH SU RA VAO
# ======================================


elif page == "Lịch sử ra vào":

    st.header("📋 LỊCH SỬ RA VÀO")

    keyword = st.text_input(
        "Tìm kiếm khách hàng"
    )

    history = visit_history(500)

    filtered = [
        row for row in history
        if keyword.lower() in (
            row["customer_code"]
            + " "
            + row["full_name"]
        ).lower()
    ]

    if filtered:

        df = pd.DataFrame(filtered)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.success(
            f"Tìm thấy {len(filtered)} lượt ra vào."
        )

    else:

        st.info("Không tìm thấy dữ liệu.")



# ======================================
# 8. AI AGENT
# ======================================

elif page == "AI Agent":

    st.header("🤖 Trợ lý AI Customer Agent")

    st.write(
        "Nhập câu hỏi để tra cứu thông tin "
        "khách hàng và hoạt động ra vào."
    )

    question = st.text_input(
        "Câu hỏi của bạn",
        placeholder="Ví dụ: Có bao nhiêu khách đang trong phòng?"
    )

    if st.button("Gửi câu hỏi"):

        if question.strip():

            answer = agent.answer_question(question)

            st.success("Kết quả trả lời")

            st.write(answer)

        else:

            st.warning(
                "Bạn chưa nhập câu hỏi."
            )


# ======================================
# 9. CHAN TRANG
# ======================================

st.sidebar.divider()

st.sidebar.caption(
    "AI Customer Agent - Python Project"
)
