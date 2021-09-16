import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

def get_graph():
    buffer=BytesIO()
    plt.savefig(buffer,format='png')
    buffer.seek(0)
    image_png=buffer.getvalue()
    graph=base64.b64encode(image_png)
    graph=graph.decode('utf-8')
    buffer.close()
    return graph

def get_pie_plot(data,labels,title):
    plt.switch_backend('AGG')


    # Creating explode data
    # explode = (0.1, 0.0)

    # Creating color parameters
    colors = ("orange", "cyan", "brown",
              "grey", "indigo", "beige")

    # Wedge properties
    wp = {'linewidth': 1, 'edgecolor': "green"}

    # Creating autocpt arguments
    def func(pct, allvalues):
        absolute = float(pct / 100. * np.sum(allvalues))
        return "{:.1f}%\n({:.2f})".format(pct, absolute)

    # Creating plot
    fig, ax = plt.subplots(figsize=(8, 4.5))
    wedges, texts, autotexts = ax.pie(data,
                                      autopct=lambda pct: func(pct, data),

                                      labels=labels,
                                      shadow=True,
                                      colors=colors,
                                      startangle=90,
                                      wedgeprops=wp,
                                      textprops=dict(color="black"))

    # Adding legend
    ax.legend(wedges, labels,
              # title="Cars",
              loc="best",
              bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title(title)

    # show plot
    # plt.show()
    # plt.figure(figsize=(10,5))
    # plt.title("Teacher Count VS Student Count")
    # plt.pie(data,labels=labels)
    # plt.show()
    plt.tight_layout()
    graph=get_graph()
    return graph
def courses_bar_chart(courses,values,person):
    # plt.switch_backend('AGG')
    # plt.figure(figsize=(8, 4.5))
    # plt.bar(courses,values,kind='barh')
    # plt.title("Students Enrolled in Different Courses")
    # Figure Size
    fig, ax = plt.subplots(figsize=(10, 5))

    # Horizontal Bar Plot
    ax.barh(courses, values,color=['red', 'blue', 'purple', 'green', 'lavender','skyblue'])

    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)

    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)

    # Add x, y gridlines
    ax.grid(b=True, color='grey',
            linestyle='-.', linewidth=0.5,
            alpha=0.2)

    # Show top values
    ax.invert_yaxis()

    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width() + 0.2, i.get_y() + 0.5,
                 str(round((i.get_width()), 2)),
                 fontsize=10, fontweight='bold',
                 color='grey')

    # Add Plot Title
    ax.set_title(person+' Registered in each Course',
                 loc='left', )


    plt.tight_layout()
    graph = get_graph()
    return graph
def attendance_pie_chart(labels,values):
    plt.figure(figsize=(10, 5))
    plt.title("Attendance Performance Chart")
    plt.xlabel('Dates')
    plt.ylabel('Number of Students Present')
    plt.plot(labels,values)
    plt.tight_layout()
    graph = get_graph()
    return graph
def quiz_analytics_bar(lables,values,title):
    fig, ax = plt.subplots(figsize=(10, 2))

    # Horizontal Bar Plot
    ax.barh(lables, values,color=['green'])

    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)

    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)

    # Add x, y gridlines
    ax.grid(b=True, color='grey',
            linestyle='-.', linewidth=0.5,
            alpha=0.2)

    # Show top values
    ax.invert_yaxis()

    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width() + 0.2, i.get_y() + 0.5,
                 str(round((i.get_width()), 2)),
                 fontsize=10, fontweight='bold',
                 color='grey')

    # Add Plot Title
    ax.set_title(title,
                 loc='left', )

    plt.tight_layout()
    graph = get_graph()
    return graph
def quiz_analytics_bar(lables,values,title,xlabel,ylabel):
    fig, ax = plt.subplots(figsize=(15, 4))

    # Horizontal Bar Plot
    ax.barh(lables, values,color=['green'])

    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)

    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)

    # Add x, y gridlines
    ax.grid(b=True, color='grey',
            linestyle='-.', linewidth=0.5,
            alpha=0.2)

    # Show top values
    ax.invert_yaxis()

    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width() + 0.2, i.get_y() + 0.5,
                 str(round((i.get_width()), 2)),
                 fontsize=10, fontweight='bold',
                 color='grey')

    # Add Plot Title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title,
                 loc='left', )

    graph = get_graph()
    return graph
def quiz_analytics_filter_bar(lables,values,title,xlabel,ylabel):
    fig, ax = plt.subplots(figsize=(12, 4))

    # Horizontal Bar Plot
    ax.barh(lables, values,color=['green'])

    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)

    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)

    # Add x, y gridlines
    ax.grid(b=True, color='grey',
            linestyle='-.', linewidth=0.5,
            alpha=0.2)

    # Show top values
    ax.invert_yaxis()

    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width() + 0.05, i.get_y() + 0.5,
                 str(round((i.get_width()), 2)),
                 fontsize=10, fontweight='bold',
                 color='grey')

    # Add Plot Title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title,
                 loc='left', )

    graph = get_graph()
    return graph