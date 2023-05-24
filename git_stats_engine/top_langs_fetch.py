
import requests
import io
import matplotlib.pyplot as plt
from fastapi import Response



# A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query, headers):
    request = requests.post('https://api.github.com/graphql',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}. {query}")

def func(pct):
  return "{:1.1f}%".format(pct)

def pie_chart(lang_data):

    plt.figure(figsize=(15, 19))
    plt.pie(lang_data.values(), labels= lang_data.keys(), autopct=lambda pct: func(pct))
    plt.legend(title = "Top Langs")

    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='svg')
    bytes_image.seek(0)
    c = bytes_image.read()
    return c


def bar_plot(lang_data):


    plt.figure(figsize=(5, 9))
    plt.bar(range(len(lang_data)), list(lang_data.values()), align='center')
    plt.xticks(range(len(lang_data)), list(
        lang_data.keys()), rotation='vertical')

    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='svg')
    bytes_image.seek(0)
    c = bytes_image.read()
    return c


async def top_langs(headers, username: str, noOfRepos : int, lang_count : int, layout):
    
    # TODO: LOOK THIS
    variables = {
        "username": username,
        "noOfRepos": noOfRepos,
        "langCount": lang_count
    }

    # The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.
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

    for repo in result["data"]["user"]["repositories"]["nodes"]:

        for lang in repo["languages"]["edges"]:

            # print("name is {},  size is {}".format(
            #     lang["node"]["name"], lang["size"]))
            # print("language is {}, size is {}".format(l, s))
            l = lang["node"]["name"]
            s = lang["size"]

            total += s

            if l not in lang_data:
                lang_data[l] = s
            else:
                lang_data[l] += s


    sorted_data = {k: v for k, v in sorted(lang_data.items(), key=lambda item: item[1], reverse=True)}

    # draw = pie_chart
    match layout:
        case 'pie':
            draw = pie_chart
        case 'bar':
            draw = bar_plot
        case _:
            draw = pie_chart

    return Response(content=draw(sorted_data), media_type='image/svg+xml; charset=utf-8')
