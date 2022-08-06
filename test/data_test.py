


def index(request):
    try:
        url = "https://www.hetzner.com/a_hz_serverboerse/live_data.json"
        s = requests.session()
        s.keep_alive = False

        r = requests.post(url, verify=False, timeout=5)

        data = r.json()['server']
        p = Paginator(data, 20)
        pn = request.GET.get('page')
        page_obj = p.get_page(pn)
        context = {
            'data': data,
            'page_obj': page_obj
        }
        return render(request, 'index.html', context)


    except requests.exceptions.ConnectionError as e:
        return HttpResponse({e})
