# plot_info = dict(plot=True,  # 是否绘制
#                  subplot=True,  # 是否绘制成子图
#                  plotname='',  # 图形名称
#                  plotabove=False,  # 子图是否绘制在主图的上方
#                  plotlinelabels=False,  # 主图上曲线的名称
#                  plotlinevalues=True,  # 是否展示曲线最后一个时间点上的取值
#                  plotvaluetags=True,  # 是否以卡片的形式在曲线末尾展示最后一个时间点上的取值
#                  plotymargin=0.0,  # 用于设置子图 y 轴的边界
#                  plothlines=[a, b, ...],  # 用于绘制取值为 a,b,... 的水平线
#                  plotyticks=[],  # 用于绘制取值为 a,b,... y轴刻度
#                  plotyhlines=[a, b, ...],  # 优先级高于plothlines、plotyticks，是这两者的结合
#                  plotforce=False,  # 是否强制绘图
#                  plotmaster=None,  # 用于指定主图绘制的主数据
#                  plotylimited=True,
#                  # 用于设置主图的 y 轴边界，
#                  # 如果True，边界只由主数据 data feeds决定，无法完整显示超出界限的辅助指标；
#                  # 如果False, 边界由主数据 data feeds和指标共同决定，能确保所有数据都能完整展示
#                  )
import webbrowser

if __name__ == '__main__':
    webbrowser.open("D:\\work\\git\\Tools\static\\analyze\\pyfolio_BNBUSDT_1hbgvLZgNg6dWYafDa.html")