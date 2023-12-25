# @author xiaoyu
# @date 2023/12/22
# @file home.py
import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import jieba
import streamlit as st
from pyecharts.charts import WordCloud, Funnel, Radar, Bar, Line, Pie, Scatter
from pyecharts.globals import ThemeType
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts

def getdata_base_text(url):
    """
    :param url: 浏览器地址
    :return: 以字符串的形式返回一个文本
    """
    response = requests.get(url)
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
    text = soup.get_text()
    return text

def ut_get_first_n_indict(dct, n):
    # 获取字典中前n个键值对
    first_n_elements = {key: dct[key] for key in list(dct)[:n]}
    return first_n_elements

def remove_html_punctuation(text):
    '''
    :param text: 需要除去html标签和标点的文本
    :return: 返回清楚好的文本
    '''
    clean_text1 = re.sub(r'<.*?>', '', text) #利用正侧表达式清除html标签
    clean_text2 = re.sub(r'[^\w\s]', '', clean_text1)#利用正侧表达式清除标点符号标签
    clean_text3 = re.sub(r'\s{1,}', ' ', clean_text2)#利用正侧表达式清除一个及以上的空格标签
    return clean_text3

#分词并统计词频
def tokenize_and_count(text):
    '''
    :param text: 分词并统计词频的文本
    :return: 返回Counter类型。里面包含了结果
    '''
    words = jieba.lcut(text)  #利用jieba分词
    filtered_words = [word for word in words if 2 <= len(word)]  #清洗字数为1的词语
    word_count = Counter(filtered_words)#类型转化
    return word_count

def del_key_web_word(url):
    """
    :param text:从一个文本里面得到出现次数最多的
    :return: 以字典的形式返回网站中出现次数前30的关键词
    """
    # 去除标点符号
    text=getdata_base_text(url)
    clead_text=remove_html_punctuation(text)
    word_count=tokenize_and_count(clead_text)
    #取前30个词语
    top_words = word_count.most_common(30)
    keywords = dict(top_words)
    return keywords

def del_key_self_word(url):
    '''
    :param url: 用户输入的地址
    :param st: streamlit对象st
    :return:
    '''
    #返回的字典
    item_counts = {}
    #输入
    key_ower = st.text_input("输入自己需要的关键词(可以以逗号、空格分开)")
    #除去逗号 空格
    items = re.split(r'[,，\s]+', key_ower)
    #过滤掉原始列表 items 中的空字符串元素，并且将每个非空元素两端的空白字符去除
    items = [item.strip() for item in items if item.strip()]
    #得到原始数据
    text = getdata_base_text(url)
    # 遍历列表中的每个元素
    for item in items:
        # 使用 count() 方法统计元素在文本中出现的次数，并存储到字典中
        item_counts[item] = text.lower().count(item.lower())
    return item_counts

def tb_generate(chart_type, keyword_counts):
    if chart_type == "折线图":
        line_chart=Line()
        line_chart.add_xaxis(list(keyword_counts.keys()))
        line_chart.add_yaxis("", list(keyword_counts.values()))
        line_chart.set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
            title_opts=opts.TitleOpts(title=""),
            visualmap_opts=opts.VisualMapOpts(max_=150),
            toolbox_opts=opts.ToolboxOpts(),)
        st_pyecharts(line_chart)
    elif chart_type == "饼图":
        pie_chart=Pie()
        pie_chart.add("", [list(z) for z in zip(keyword_counts.keys(), keyword_counts.values())])
        pie_chart.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        pie_chart.set_global_opts(title_opts=opts.TitleOpts(title=""), toolbox_opts=opts.ToolboxOpts(),visualmap_opts=opts.VisualMapOpts(max_=150),)
        st_pyecharts(pie_chart)
    elif chart_type == "柱状图":
        bar_chart=Bar()
        bar_chart.add_xaxis(list(keyword_counts.keys()))
        bar_chart.add_yaxis("", list(keyword_counts.values()))
        bar_chart.set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                title_opts=opts.TitleOpts(title=""),
                visualmap_opts=opts.VisualMapOpts(max_=150),
                toolbox_opts=opts.ToolboxOpts(),)
        st_pyecharts(bar_chart)
    elif chart_type == "散点图":
        scatter_chart=Scatter()
        scatter_chart.add_xaxis(list(keyword_counts.keys()))
        scatter_chart.add_yaxis("", list(keyword_counts.values()))
        scatter_chart.set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                title_opts=opts.TitleOpts(title=""),
                visualmap_opts=opts.VisualMapOpts(max_=150),
                toolbox_opts=opts.ToolboxOpts(),)
        st_pyecharts(scatter_chart)
    elif chart_type == "面积图":
        mianji_chart = Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        mianji_chart.add_xaxis(list(keyword_counts.keys()))
        mianji_chart.add_yaxis("Counts", list(keyword_counts.values()), is_smooth=True,
                               areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
        mianji_chart.set_global_opts(title_opts=opts.TitleOpts(title="面积图"))
        st_pyecharts(mianji_chart)
    elif chart_type == "雷达图":
        radar_chart = Radar()
        radar_chart.add_schema(schema=[opts.RadarIndicatorItem(name=key, max_=150) for key in keyword_counts.keys()])
        radar_chart.add("", [list(keyword_counts.values())], color="blue")
        radar_chart.set_global_opts(title_opts=opts.TitleOpts(title="Radar Chart"), toolbox_opts=opts.ToolboxOpts())
        st_pyecharts(radar_chart)
    elif chart_type == "漏斗图":
        funnel_chart = Funnel()
        funnel_chart.add("", [list(z) for z in zip(keyword_counts.keys(), keyword_counts.values())])
        funnel_chart.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        funnel_chart.set_global_opts(title_opts=opts.TitleOpts(title=""), toolbox_opts=opts.ToolboxOpts(),)
        st_pyecharts(funnel_chart)


# 绘制词云
def plot_word_cloud(word_count, shape='circle'):
    wordcloud = (
        WordCloud()
        .add("", word_count.most_common(20), word_size_range=[30, 100], shape=shape)
        .set_global_opts(title_opts=opts.TitleOpts(title="词云"))
    )
    return wordcloud

#横拉框
def horizon_pull_frame(counter):
    max_count = max(counter.values())
    min_count = st.sidebar.slider('最小计数值', 0, max_count, 0)
    max_count = st.sidebar.slider('最大计数值', min_count, max_count, max_count)
    cleaned_counter = Counter({key: value for key, value in counter.items() if min_count <= value <= max_count})
    return cleaned_counter

def ciyun():
    st.title("词云绘制示例")
    # 下拉框选择词云形状
    shape_options = ['circle', 'rect', 'roundRect', 'ellipse', 'triangle']
    url = st.text_input("输入网址", "https://www.gov.cn/xinwen/2022-10/25/content_5721685.htm")
    selected_shape = st.selectbox("选择词云形状", shape_options)
    text = getdata_base_text(url)
    clear_text=remove_html_punctuation(text)
    word_count=tokenize_and_count(clear_text)
    clear_number_text=horizon_pull_frame(word_count)
    # 绘制词云
    word_cloud = plot_word_cloud(clear_number_text, shape=selected_shape)
    # 保存词云为 HTML 文件
    html_file = "word_cloud.html"
    word_cloud.render(html_file)
    # 在Streamlit中显示词云
    st.components.v1.html(open(html_file, 'r').read(), height=500, width=900, scrolling=True)

def data_analysis():
    # 设置页面标题
    st.title("网页关键词分析")
    # 添加文本输入框，让用户输入URL
    url = st.text_input("输入网址", "https://www.gov.cn/xinwen/2022-10/25/content_5721685.htm")
    # 添加下拉框，让用户选择图表类型
    chart_type = st.sidebar.selectbox("Select Chart Type", ["折线图", "饼图", "柱状图", "散点图", "直方图", "区域图", "热力图"])
    keywords=del_key_web_word(url)
    # 创建一个多选下拉菜单
    keys_list = list(keywords.keys())
    selected_options = st.sidebar.multiselect(
        "选择你想要分析的关键词:",
        keys_list
    )
    #用户自己输入关键词
    dict2=del_key_self_word(url)
    dict1 = {option: keywords.get(option) for option in selected_options if option in keywords}
    dict_end= {key: value for d in [dict1, dict2] for key, value in d.items()}  # 合并字典1和字典2
    # 添加按钮，点击后进行统计和绘图
    if st.button("分析"):
        if not dict_end:
            dict_end =ut_get_first_n_indict(keywords, 8)
        tb_generate(chart_type,dict_end)

def pa_sidebar(wide=None,hige=None):
    #侧边栏标题
    st.sidebar.title("数据")
    #侧边栏选项
    list_baidu_project=["词云","数据图表"]
    selected_option = st.sidebar.selectbox("",list_baidu_project)
    # 根据侧边栏选择显示不同的内容
    if selected_option == "词云":
        ciyun()
    elif selected_option == "数据图表":
        data_analysis()

# 运行主函数
if __name__ == '__main__':
    pa_sidebar()
