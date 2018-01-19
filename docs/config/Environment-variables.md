Переменные окружения
=======
Есть только одна переменная окружения с фиксированным именем (остальные задаются через файл конфигурации)
### CROSSPM_CONFIG_PATH
- Значение этой переменной указывает на расположение файла конфигурации. Если в переменной указан полный путь вместе с именем файла - берется этот файл, если другой не задан в параметрах командной строки. Если в переменной указан только путь без имени файла, то по указанному пути ищется файл **crosspm.yaml**
- По указанному в этой переменной пути, также происходит поиск импортируемых файлов конфигурации, указанных в разделе import основного файла конфигурации.
- В этой переменной может быть указано несколько путей, разделенных знаком ";". В таком случае, если одно из этих значений - полный путь с именем файла, то crosspm попытается использовать именно его.
- При указании полного пути с именем файла, нет необходимости добавлять этот путь еще раз для поиска импортируемых файлов - crosspm сделает это сам.
- Глобальный файл конфигурации так же ищется по путям, указанным в этой переменной. Его имя файла должно быть одним из двух вариантов: **crosspm_global.yaml** или **global.yaml**