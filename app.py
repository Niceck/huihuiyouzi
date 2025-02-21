import streamlit as st
import tushare as ts
import pandas as pd
import datetime as dt

# 设置页面配置（不使用背景图）
st.set_page_config(page_title="Stock Analysis App", layout="wide")

# ------------------ Tushare 初始化 ------------------
# 请确保 secrets.toml 中配置了 Tushare Token，否则直接修改 "your_default_token_here"
tushare_token = st.secrets.get("api_keys", {}).get("tushare_token", "your_default_token_here")
ts.set_token(tushare_token)
pro = ts.pro_api()


# ================== 功能1：游资数据查询 ==================
def query_youzidata():
    st.subheader("游资数据查询")
    # 输入参数
    trade_date = st.text_input("交易日期（格式：YYYYMMDD）", value="")
    ts_code = st.text_input("股票代码", value="")
    hm_name = st.text_input("游资名称", value="")
    start_date = st.text_input("开始日期（格式：YYYYMMDD）", value="")
    end_date = st.text_input("结束日期（格式：YYYYMMDD）", value="")
    limit = st.number_input("查询的最大数据条数", min_value=1, value=500)

    if st.button("查询游资数据", key="btn_youzidata"):
        df = pro.hm_detail(
            trade_date=trade_date,
            ts_code=ts_code,
            hm_name=hm_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=0,
            fields=["trade_date", "ts_code", "ts_name", "buy_amount", "sell_amount", "net_amount", "hm_name"]
        )
        if df.empty:
            st.info("未获取到任何数据。")
        else:
            # 转换金额为单位万（整除）
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


# ================== 功能2：董秘问答查询 ==================
def get_qa_sz(ts_code, trade_date):
    try:
        df = pro.irm_qa_sz(
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


def query_dongmi():
    st.subheader("董秘问答查询")
    ts_code_input = st.text_input("股票代码（可留空）", value="")
    trade_date = st.date_input("交易日期", value=dt.datetime.today().date())
    trade_date_str = trade_date.strftime("%Y%m%d") if trade_date else ""
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
    trade_date = st.date_input("请选择交易日期", value=dt.datetime.today())
    trade_date_str = trade_date.strftime("%Y%m%d")
    if st.button("查询涨停题材列表", key="btn_limit_cpt_list"):
        try:
            df = pro.limit_cpt_list(
                trade_date=trade_date_str,
                ts_code="",
                start_date="",
                end_date="",
                limit="",
                offset="",
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


# ================== 主函数 ==================
def main():
    st.title("恢恢数据库 - 综合查询")
    # 使用 st.tabs 实现上方横向选择模块
    tabs = st.tabs(["游资数据查询", "董秘问答查询", "涨停题材列表", "题材成分股查询"])

    with tabs[0]:
        query_youzidata()
    with tabs[1]:
        query_dongmi()
    with tabs[2]:
        query_limit_cpt_list()
    with tabs[3]:
        query_ths_member()


if __name__ == "__main__":
    main()
