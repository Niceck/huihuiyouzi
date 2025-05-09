import streamlit as st
import os
import pandas as pd
import datetime as dt

# 设置页面配置（不使用背景图）
st.set_page_config(page_title="Stock Analysis App", layout="wide")

# ------------------ Tushare 初始化 ------------------
# 请确保 secrets.toml 中配置了 Tushare Token，否则直接修改 "your_default_token_here"


tushare_token = os.getenv("TUSHARE_TOKEN") or st.secrets.get("api_keys", {}).get("tushare_token", "your_default_token_here")


# ------------------ 公众号信息展示 ------------------
def show_public_account_info():
    st.markdown("## 关注我的公众号")
    # 显示公众号链接，点击后可跳转到公众号主页（请替换为你的实际链接）
    st.markdown("每日更新游资涨停题材可视化分析")
    # 展示二维码图片，请将路径替换为实际的二维码图片路径
    st.image("公众号二维码.jpg", caption="公众号二维码", width=200)

# ================== 功能1：游资数据查询 ==================
def query_youzidata():
    st.subheader("游资数据查询")
    trade_date = st.text_input("交易日期（格式：YYYYMMDD）", value="", key="youzi_trade_date")
    ts_code = st.text_input("股票代码", value="", key="youzi_ts_code")
    hm_name = st.text_input("游资名称", value="", key="youzi_hm_name")
    start_date = st.text_input("开始日期（格式：YYYYMMDD）", value="", key="youzi_start_date")
    end_date = st.text_input("结束日期（格式：YYYYMMDD）", value="", key="youzi_end_date")
    limit = st.number_input("查询的最大数据条数", min_value=1, value=500, key="youzi_limit")

    if st.button("查询游资数据", key="btn_youzidata"):
        df = pro.hm_detail(
            trade_date=trade_date,
            ts_code=ts_code,
            hm_name=hm_name,
            start_date=start_date,
            end_date=end_date,
            limit=500,
            fields=["trade_date", "ts_code", "ts_name", "buy_amount", "sell_amount", "net_amount", "hm_name"]
        )
        if df.empty:
            st.info("未获取到任何数据。")
        else:
            df['buy_amount'] = df['buy_amount'] // 10000
            df['sell_amount'] = df['sell_amount'] // 10000
            df['net_amount'] = df['net_amount'] // 10000
            df.rename(columns={
                'trade_date': '交易日期',
                'ts_code': '股票代码',
                'ts_name': '股票名称',
                'buy_amount': '买入金额(万)',
                'sell_amount': '卖出金额(万)',
                'net_amount': '净买入金额(万)',
                'hm_name': '游资名称'
            }, inplace=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

# ------------------ 获取董秘问答数据 ------------------
def get_qa_sz(ts_code, trade_date):
    try:
        df = pro.irm_qa_sz(
            ts_code=ts_code,
            trade_date=trade_date,
            limit=500,
            fields="ts_code,name,q,a,pub_time"
        )
        df.rename(columns={
            'ts_code': '股票代码',
            'name': '股票名称',
            'q': '提问',
            'a': '回答',
            'pub_time': '发布时间'
        }, inplace=True)
        return df
    except Exception as e:
        st.error(f"获取深圳数据失败: {e}")
        return pd.DataFrame()

def get_qa_sh(ts_code, trade_date):
    try:
        df = pro.irm_qa_sh(
            ts_code=ts_code,
            trade_date=trade_date,
            fields="ts_code,name,q,a,pub_time"
        )
        df.rename(columns={
            'ts_code': '股票代码',
            'name': '股票名称',
            'q': '提问',
            'a': '回答',
            'pub_time': '发布时间'
        }, inplace=True)
        return df
    except Exception as e:
        st.error(f"获取上海数据失败: {e}")
        return pd.DataFrame()

# ================== 功能2：董秘问答查询 ==================
def query_dongmi():
    st.subheader("董秘问答查询")
    ts_code_input = st.text_input("股票代码（可留空）", value="", key="dongmi_ts_code")
    # 使用文本输入框代替日期选择控件，用户可自行输入日期，或者留空
    trade_date_str = st.text_input("交易日期（格式：YYYYMMDD，可选）", value="", key="dongmi_trade_date")
    if st.button("查询董秘问答", key="btn_dongmi"):
        st.write("### 深圳数据")
        df_sz = get_qa_sz(ts_code_input, trade_date_str)
        if not df_sz.empty:
            df_sz.index = range(1, len(df_sz) + 1)
            st.dataframe(df_sz, use_container_width=True)
        else:
            st.info("未获取到深圳数据。")
        st.write("### 上海数据")
        df_sh = get_qa_sh(ts_code_input, trade_date_str)
        if not df_sh.empty:
            df_sh.index = range(1, len(df_sh) + 1)
            st.dataframe(df_sh, use_container_width=True)
        else:
            st.info("未获取到上海数据。")


# ================== 功能3：涨停题材列表 ==================
def query_limit_cpt_list():
    st.subheader("涨停题材列表")
    trade_date = st.date_input("请选择交易日期", value=dt.datetime.today(), key="limit_trade_date")
    trade_date_str = trade_date.strftime("%Y%m%d")
    if st.button("查询涨停题材列表", key="btn_limit_cpt_list"):
        try:
            df = pro.limit_cpt_list(
                trade_date=trade_date_str,
                ts_code="",
                start_date="",
                end_date="",
                limit="500",
                fields=[
                    "ts_code",
                    "name",
                    "trade_date",
                    "days",
                    "up_stat",
                    "cons_nums",
                    "up_nums",
                    "rank"
                ]
            )
            if df.empty:
                st.info("未查询到数据")
            else:
                df.rename(columns={
                    "ts_code": "题材代码",
                    "name": "题材名称",
                    "trade_date": "交易日期",
                    "days": "连续天数",
                    "up_stat": "涨停状态",
                    "cons_nums": "连板家数",
                    "up_nums": "涨停数量",
                    "rank": "排名"
                }, inplace=True)
                df = df.sort_values(by="排名", ascending=True).reset_index(drop=True)
                df.index = range(1, len(df) + 1)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"查询失败：{e}")

# ================== 功能4：题材成分股查询 ==================
def query_ths_member():
    st.subheader("题材成分股查询")
    ts_code_input = st.text_input("请输入题材代码", key="ths_input")
    if st.button("查询题材成分股", key="btn_ths_member"):
        if ts_code_input.strip() == "":
            st.info("请先输入题材代码再进行查询。")
        else:
            try:
                df = pro.ths_member(
                    ts_code=ts_code_input,
                    limit="500",
                    fields=[
                        "ts_code",
                        "con_code",
                        "con_name"
                    ]
                )
                if df.empty:
                    st.info("未查询到数据")
                else:
                    df.rename(columns={
                        "ts_code": "题材代码",
                        "con_code": "成分股代码",
                        "con_name": "成分股名称"
                    }, inplace=True)
                    df = df.reset_index(drop=True)
                    df.index = range(1, len(df) + 1)
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"查询失败：{e}")

# ================== 功能5：概念题材查询 ==================
def query_concept_data():
    st.subheader("概念题材查询")
    trade_date = st.text_input("交易日期（格式：YYYYMMDD）", value="", key="concept_trade_date")
    if st.button("查询概念题材数据", key="btn_concept"):
        try:
            df = pro.kpl_concept(
                trade_date=trade_date,
                ts_code="",
                name="",
                limit="500",
                fields=[
                    "trade_date",
                    "ts_code",
                    "name",
                    "z_t_num",
                    "up_num"
                ]
            )
            if df.empty:
                st.info("未查询到数据")
            else:
                df.rename(columns={
                    "ts_code": "题材代码",
                    "name": "题材名称",
                    "trade_date": "交易日期",
                    "z_t_num": "涨停家数",
                    "up_num": "升温家数"
                }, inplace=True)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"查询失败：{e}")

# ================== 功能6：题材成分股查询（概念） ==================
def query_concept_cons():
    st.subheader("题材成分股查询")
    ts_code_input = st.text_input("题材代码", key="ths_input_concept")
    trade_date = st.text_input("交易日期（格式：YYYYMMDD）", value="", key="concept_cons_trade_date")
    if st.button("查询题材成分股数据", key="btn_concept_cons"):
        try:
            df = pro.kpl_concept_cons(
                ts_code=ts_code_input,
                trade_date=trade_date,
                con_code="",
                limit="500",
                fields=[
                    "ts_code",
                    "name",
                    "con_name",
                    "con_code",
                    "trade_date",
                    "desc",
                    "hot_num"
                ]
            )
            if df.empty:
                st.info("未查询到数据")
            else:
                df.rename(columns={
                    "ts_code": "题材代码",
                    "name": "题材名称",
                    "con_name": "成分股名称",
                    "con_code": "成分股代码",
                    "trade_date": "交易日期",
                    "desc": "描述",
                    "hot_num": "人气值"
                }, inplace=True)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"查询失败：{e}")

# ================== 功能7：连板天数查询 ==================
def query_limit_step():
    st.subheader("连板天数查询")
    trade_date = st.text_input("交易日期（格式：YYYYMMDD）", value="", key="limit_step_trade_date")
    ts_code_input = st.text_input("股票代码", value="", key="limit_step_ts_code")
    nums = st.text_input("连板次数（例如：2,3）", value="", key="limit_step_nums")
    if st.button("查询连板天数", key="btn_limit_step"):
        try:
            df = pro.limit_step(
                trade_date=trade_date,
                ts_code=ts_code_input,
                start_date="",
                end_date="",
                nums=nums,
                limit="500",
                fields=[
                    "ts_code",
                    "name",
                    "trade_date",
                    "nums"
                ]
            )
            if df.empty:
                st.info("未查询到数据")
            else:
                df.rename(columns={
                    "ts_code": "股票代码",
                    "name": "股票名称",
                    "trade_date": "交易日期",
                    "nums": "连板天数"
                }, inplace=True)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"查询失败：{e}")

# ================== 功能8：机构调研 ==================
def query_stk_surv():
    st.subheader("机构调研")
    ts_code_input = st.text_input("股票代码", value="", key="stk_surv_ts_code")
    trade_date = st.text_input("交易日期（格式：YYYYMMDD）", value="", key="stk_surv_trade_date")
    start_date = st.text_input("开始日期（格式：YYYYMMDD）", value="", key="stk_surv_start_date")
    end_date = st.text_input("结束日期（格式：YYYYMMDD）", value="", key="stk_surv_end_date")
    if st.button("查询存续公告", key="btn_stk_surv"):
        try:
            df = pro.stk_surv(
                ts_code=ts_code_input,
                trade_date=trade_date,
                start_date=start_date,
                end_date=end_date,
                limit="500",
                fields=[
                    "ts_code",
                    "name",
                    "surv_date",
                    "fund_visitors",
                    "rece_place",
                    "rece_org",
                    "org_type",
                    "comp_rece",
                    "content"
                ]
            )
            if df.empty:
                st.info("未查询到数据")
            else:
                df.rename(columns={
                    "ts_code": "股票代码",
                    "name": "股票名称",
                    "surv_date": "公告日期",
                    "fund_visitors": "参会人员",
                    "rece_place": "会场",
                    "rece_org": "接待机构",
                    "org_type": "机构类型",
                    "comp_rece": "公司接待",
                    "content": "内容"
                }, inplace=True)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"查询失败：{e}")

# ================== 主函数 ==================
def main():
    # 使用两列布局，左侧放标题，右侧放公众号信息
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("柚子侦探数据库 - 综合查询")
        st.write("")  # 标题下空一行
        st.markdown("请大家常关注我的公众号，使用工具。后续如工具地址有变化，公众号将第一时间更新信息，防止工具丢失。")
        st.markdown("如有其他数据需求、问题或建议，欢迎通过公众号联系我，我将不断改进和完善工具。")
        st.markdown("（交易日下午17点左右更新）")
    with col2:
        show_public_account_info()


    tabs = st.tabs([
        "游资数据",
        "董秘问答",
        "同花顺题材",
        "同花顺成分股",
        "开市啦题材",
        "开市啦成分股",
        "连板天数查询",
        "机构调研"
    ])

    with tabs[0]:
        query_youzidata()
    with tabs[1]:
        query_dongmi()
    with tabs[2]:
        query_limit_cpt_list()
    with tabs[3]:
        query_ths_member()
    with tabs[4]:
        query_concept_data()
    with tabs[5]:
        query_concept_cons()
    with tabs[6]:
        query_limit_step()
    with tabs[7]:
        query_stk_surv()

if __name__ == "__main__":
    main()
