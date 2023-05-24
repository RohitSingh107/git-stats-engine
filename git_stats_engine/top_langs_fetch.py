
import requests
import io
import matplotlib.pyplot as plt
from fastapi import Response
import itertools as it



# A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query, headers):
    request = requests.post('https://api.github.com/graphql',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}. {query}")


def pie_chart(lang_data, sizexy : str):

    size = list(map(int,sizexy.split(',')))

    # plt.style.use('dark_background')
    plt.figure(figsize=(size[0], size[1]))
    plt.pie(lang_data.values(), labels= lang_data.keys(), autopct=lambda pct: "{:1.1f}%".format(pct))
    plt.legend(title = "Top Langs")

    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='svg', bbox_inches="tight")
    bytes_image.seek(0)
    c = bytes_image.read()
    return c


def donut_chart(lang_data, sizexy : str):
    # plt.style.use('dark_background')

    size = list(map(int,sizexy.split(',')))
    explode = [0.05 for _ in range(len(lang_data))]

    plt.figure(figsize=(size[0], size[1]))
    plt.pie(lang_data.values(), labels= lang_data.keys(), autopct=lambda pct: "{:1.1f}%".format(pct), pctdistance=0.85, explode=explode)
    plt.legend(title = "Top Langs")

    # draw circle
    centre_circle = plt.Circle((0, 0), 1, fc='white')
    fig = plt.gcf()
    # Adding Circle in Pie chart
    fig.gca().add_artist(centre_circle)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='svg', bbox_inches="tight")

    bytes_image.seek(0)
    c = bytes_image.read()
    return c


def bar_plot(lang_data, sizexy : str):

    size = list(map(int,sizexy.split(',')))
    # plt.style.use('dark_background')
    plt.figure(figsize=(size[0], size[1]))
    plt.bar(range(len(lang_data)), list(lang_data.values()), align='center')
    plt.xticks(range(len(lang_data)), list(
        lang_data.keys()), rotation='vertical')
    plt.legend(title='Size in Bytes')

    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='svg', bbox_inches="tight")
    bytes_image.seek(0)
    c = bytes_image.read()
    return c


async def top_langs(headers, username: str, lang_count : int, layout, exclude_repo : str, exclude_lang : str, sizexy: str):

    if exclude_repo == "":
        excluded_repo = set()
    else:
        excluded_repo = set(exclude_repo.split(','))

    if exclude_lang == "":
        excluded_lang = set()
    else:
        excluded_lang = set(exclude_lang.split(','))

    variables = {
        "username": username,
        "noOfRepos": 100,
        "topLangs": 10
    }

    query = """
    query userInfo($login: String = "%s") {
            user(login: $login) {
              # fetch only owner repos & not forks
              repositories(ownerAffiliations: OWNER, isFork: false, first: %s) {
                nodes {
                  name
                  languages(first: %s, orderBy: {field: SIZE, direction: DESC}) {
                    edges {
                      size
                      node {
                        color
                        name
                      }
                    }
                  }
                }
              }
            }
          }
    """



    result = run_query(query % tuple(variables.values()), headers)  # Execute the query
    lang_data : dict[str,int] = {}
    total = 0

    # exclude_lang = set(['html', 'qml', 'cmake', 'css', 'objective-c'])

    for repo in result["data"]["user"]["repositories"]["nodes"]:

        if repo["name"] in excluded_repo:
            print(f"Excluded repository: {repo['name']}")
            continue

        for lang in repo["languages"]["edges"]:

            l = lang["node"]["name"]
            if l.lower() in excluded_lang:
                print(f"Excluded language: {lang['node']['name']}")
                continue

            s = lang["size"]

            total += s

            if l not in lang_data:
                lang_data[l] = s
            else:
                lang_data[l] += s



    sorted_data = {k: v for k, v in sorted(lang_data.items(), key=lambda item: item[1], reverse=True)}

    top_sorted_data = dict(it.islice(sorted_data.items(), 0 ,lang_count))

    # draw = pie_chart
    match layout:
        case 'pie':
            draw = pie_chart
        case 'bar':
            draw = bar_plot
        case 'donut':
            draw = donut_chart
        case _:
            draw = pie_chart

    return Response(content=draw(top_sorted_data, sizexy), media_type='image/svg+xml; charset=utf-8')
