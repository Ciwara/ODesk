# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import json
import csv

from django.conf import settings


def read_csv(file, json_file, format=""):
    csv_rows = []
    file = get_path("data,{}".format(file))
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        title = reader.fieldnames
        for row in reader:
            csv_rows.extend(
                [{title[i]:row[title[i]] for i in range(len(title))}])
        write_json(csv_rows, json_file, format)


def write_json(data, json_file, format):
    with open(json_file, "w") as f:
        f.write(json.dumps(data))


def get_path(path_):
    return os.path.join(settings.BASE_ODK_DIR, *path_.split(','))


def get_odk_data(form):
    # with open(config_file) as config_f:
    #     data = json.loads(config_f.read())
    # print(config_f)
    # export_start_date = data.get("start_on")
    # export_end_date = TODAY.strftime("%Y/%m/%d")
    # data = data[0]
    print("getting data for ODK Server {}...".format(
          "with media files " if form.exclude_media_export else ""))
    default_params = "java -jar {app} --form_id {form_id} --odk_username {odk_username} --odk_password {odk_password} --overwrite_csv_export --export_directory {export_directory} --storage_directory {storage_directory} --aggregate_url {aggregate_url} --export_filename {export_filename}".format(
        app=get_path(form.odk_setting.app),
        form_id=form.form_id,
        odk_username=form.odk_setting.odk_username,
        odk_password=form.odk_setting.odk_password,
        export_directory=get_path(form.odk_setting.export_directory),
        storage_directory=get_path(form.odk_setting.storage_directory),
        export_filename=form.export_filename,
        aggregate_url=form.odk_setting.aggregate_url)

    if form.exclude_media_export:
        default_params += " --exclude_media_export"
    os.system(default_params)
