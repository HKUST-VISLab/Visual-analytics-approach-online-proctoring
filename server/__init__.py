from flask import Flask
from flask import request
from flask_cors import CORS
import pymongo 
from flask_pymongo import PyMongo
import json
from pydash import _
import numpy as np
import pandas as pd


STATIC_FOLDER = 'server/static'
# STATIC_FOLDER = '../client/dist'
TEMPLATE_FOLDER = '../client/dist'

app = Flask(__name__, static_url_path='', static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
app.config.from_object('config')
CORS(app)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/proctoring"
# mongo = PyMongo(app)

abandon_student_list = ['128126_A', '128126_B', '141137_B']


from server.routes import index

def get_one_axis_mouse(x, axis):
    return {
        "timestamp": x["d_timestamp"],
        axis: x[f"screen{axis}_scaled"]
    }

def get_one_axis_bbox(x, axis):
    return {
        "timestamp": x["d_timestamp"],
        f"{axis}_min": x[f"{axis}_min_scaled"],
        f"{axis}_max": x[f"{axis}_max_scaled"],
    }

def get_one_axis_headpose(x, axis):
    return {
        "timestamp": x["d_timestamp"],
        axis: x[f"{axis}_scaled"],
    }


with open(STATIC_FOLDER+"/mouse_raw_data_anony.json") as f:
    json_mouse_raw_data = json.load(f)

with open(STATIC_FOLDER+"/mouse_special_event_anony.json") as f:
    json_mouse_special_event = json.load(f)

with open(STATIC_FOLDER+"/student_result_list_anony.json") as f:
    json_student_result_list = json.load(f)

with open(STATIC_FOLDER+"/bbox_raw_data_anony.json") as f:
    json_bbox_raw_data = json.load(f)

with open(STATIC_FOLDER+"/headpose_raw_data_anony.json") as f:
    json_headpose_raw_data = json.load(f)

with open(STATIC_FOLDER+"/question_time_length_anony.json") as f:
    json_question_time_length = json.load(f)

with open(STATIC_FOLDER+"/mouse_raw_data_replay_anony.json") as f:
    json_mouse_raw_data_replay = json.load(f)

# student_id: dong_A1; question_id: mc_1; axis: X or Y; 
@app.route("/api/mouse_raw_data/<string:student_id>/<string:question_id>/<string:axis>", methods=['POST','GET'])
def mouse_raw_data(student_id, question_id, axis):
    return {"data": _.map(json_mouse_raw_data[student_id][question_id], lambda x: get_one_axis_mouse(x, axis))}

@app.route("/api/mouse_raw_data_replay/<string:student_id>/<string:question_id>", methods=['POST','GET'])
def mouse_raw_data_replay(student_id, question_id):
    data = json_mouse_raw_data_replay[student_id][question_id]
    tmp = []
    for item in data:
        tmp.append([item["x"], item["y"], item["d_timestamp"], item["clientX"], item["clientY"]])
    return {"data": tmp}
    
# student_id: dong_A1; question_id: mc_1; axis: X or Y; 
@app.route("/api/bbox_raw_data/<string:student_id>/<string:question_id>/<string:axis>", methods=['POST','GET'])
def bbox_raw_data(student_id, question_id, axis):
    return {"data": _.map(json_bbox_raw_data[student_id][question_id], lambda x: get_one_axis_bbox(x, axis))}

# student_id: dong_A1; question_id: mc_1; axis: yaw or pitch; 
@app.route("/api/headpose_raw_data/<string:student_id>/<string:question_id>/<string:axis>", methods=['POST','GET'])
def headpose_raw_data(student_id, question_id, axis):
    return {"data": _.map(json_headpose_raw_data[student_id][question_id], lambda x: get_one_axis_headpose(x, axis))}

@app.route("/api/mouse_special_event/<string:student_id>/<string:question_id>", methods=['POST','GET'])
def mouse_special_event(student_id, question_id):
    return {"data": json_mouse_special_event[student_id][question_id]}

@app.route("/api/student_result_list/<string:student_id>", methods=['POST','GET'])
def student_result_list(student_id):
    return {"data": json_student_result_list[student_id]}

@app.route("/api/all_result_list", methods=['POST','GET'])
def all_result_list():
    all_result_list = []
    for (k, v) in json_student_result_list.items():
        if k in abandon_student_list:
            continue
        v['student_id'] = k
        all_result_list.append(v)


    return {'data': all_result_list}

@app.route("/api/question_time_length/<string:student_id>", methods=['POST','GET'])
def question_time_length(student_id):
    return {"data":[{"question_id": k, "time_length": v} for (k, v) in json_question_time_length[student_id].items()]}

@app.route("/api/average_question_time_length/<string:question_set>", methods=['POST','GET'])
def average_question_time_length(question_set):
    all_question_time_length = []
    list_average_question_time_length = []
    list_question_id = ['mc_1', 'mc_2', 'mc_3', 'mc_4', 'mc_5', 'mc_6', 'mc_7', 'mc_8', 'mc_9', 'mc_10', 'sa_1', 'sa_2','sa_3', 'sa_4']
    for question_id in list_question_id:
        list_question_time_length = []
        for (student_id, i) in json_question_time_length.items():
            if student_id[-1]!=question_set or student_id in abandon_student_list:
                continue
            if question_id in i.keys():
                list_question_time_length.append(i[question_id])
                all_question_time_length.append(i[question_id])
            else:
                list_question_time_length.append(0)

        list_average_question_time_length.append(
            {
                'question_id': question_id,
                'average_time_length': float(np.mean(np.array(list_question_time_length)))
            }
        )
    list_average_question_time_length.append(
        {
                'question_id': "min",
                'average_time_length': float(np.min(np.array(all_question_time_length)))
        }
    )

    list_average_question_time_length.append(
        {
                'question_id': "max",
                'average_time_length': float(np.max(np.array(all_question_time_length)))
        }
    )

    return {"data": list_average_question_time_length}

# student_id: dong_A1; question_id: mc_1; axis: X or Y;  for headpose, X->yaw, Y->pitch
@app.route("/api/other_question_aggregate_data/<string:student_id>/<string:question_id>/<string:axis>/<int:bin_number>", methods=['POST','GET'])
@app.route("/api/other_question_aggregate_data/<string:student_id>/<string:question_id>/<string:axis>", methods=['POST','GET'])
def other_question_aggregate_data(student_id, question_id, axis, bin_number=10):

    all_histo_mouse = np.zeros((len(json_mouse_raw_data[student_id].keys())-1, bin_number))
    all_histo_bbox_max = np.zeros((len(json_mouse_raw_data[student_id].keys())-1, bin_number))
    all_histo_bbox_min = np.zeros((len(json_mouse_raw_data[student_id].keys())-1, bin_number))
    all_histo_headpose = np.zeros((len(json_mouse_raw_data[student_id].keys())-1, bin_number))

    mouse_count = 0
    bbox_max_count = 0
    bbox_min_count = 0
    headpose_count = 0
    
    idx = 0
   
    for (question_id_, j) in json_mouse_raw_data[student_id].items():
        if question_id_ == question_id:
            continue
        
        try:
            histo_mouse = np.histogram(pd.DataFrame.from_records(json_mouse_raw_data[student_id][question_id_])[f'screen{axis}_scaled'], range=(-1,1), bins=bin_number)[0]
            # all_histo_mouse[idx,:] = histo_mouse/np.sum(histo_mouse)

            if np.sum(histo_mouse) == 0:
                all_histo_mouse[idx,:] = np.zeros_like(histo_mouse)
            else:    
                all_histo_mouse[idx,:] = histo_mouse/np.sum(histo_mouse)
                mouse_count += 1
        except:
            print(student_id, question_id_)

        try:

            histo_bbox_max = np.histogram(pd.DataFrame.from_records(json_bbox_raw_data[student_id][question_id_])[f'{axis}_max_scaled'], range=(-1,1), bins=bin_number)[0]
            # all_histo_bbox_max[idx,:] = histo_bbox_max/np.sum(histo_bbox_max)

            if np.sum(histo_bbox_max) == 0:
                all_histo_bbox_max[idx,:] = np.zeros_like(histo_bbox_max)
            else:    
                all_histo_bbox_max[idx,:] = histo_bbox_max/np.sum(histo_bbox_max)
                bbox_max_count += 1
        except:
            print(student_id, question_id_)

        try:
            histo_bbox_min = np.histogram(pd.DataFrame.from_records(json_bbox_raw_data[student_id][question_id_])[f'{axis}_min_scaled'], range=(-1,1), bins=bin_number)[0]
            # all_histo_bbox_min[idx,:] = histo_bbox_min/np.sum(histo_bbox_min)

            if np.sum(histo_bbox_min) == 0:
                all_histo_bbox_min[idx,:] = np.zeros_like(histo_bbox_min)
            else:    
                all_histo_bbox_min[idx,:] = histo_bbox_min/np.sum(histo_bbox_min)
                bbox_min_count += 1
        except:
            print(student_id, question_id_)

        try:
            if axis == 'X':
                histo_headpose = np.histogram(pd.DataFrame.from_records(json_headpose_raw_data[student_id][question_id_])[f'yaw_scaled'], range=(-1,1), bins=bin_number)[0]
            else:
                histo_headpose = np.histogram(pd.DataFrame.from_records(json_headpose_raw_data[student_id][question_id_])[f'pitch_scaled'], range=(-1,1), bins=bin_number)[0]
            
            # all_histo_headpose[idx,:] = histo_headpose/np.sum(histo_headpose)

            if np.sum(histo_headpose) == 0:
                all_histo_headpose[idx,:] = np.zeros_like(histo_headpose)
            else:    
                all_histo_headpose[idx,:] = histo_headpose/np.sum(histo_headpose)
                headpose_count += 1
            
        except:
            print(student_id, question_id_)
        
        idx+=1
    
    return {
        "mouse": (np.sum(all_histo_mouse, 0)/mouse_count).tolist(),
        "bbox_max": (np.sum(all_histo_bbox_max, 0)/bbox_max_count).tolist(),
        "bbox_min": (np.sum(all_histo_bbox_min, 0)/bbox_min_count).tolist(),
        "headpose": (np.sum(all_histo_headpose, 0)/headpose_count).tolist()
    }

@app.route("/api/peer_aggregate_data/<string:student_id>/<string:question_id>/<string:axis>/<int:bin_number>", methods=['POST','GET'])
@app.route("/api/peer_aggregate_data/<string:student_id>/<string:question_id>/<string:axis>", methods=['POST','GET'])
def peer_aggregate_data(student_id, question_id, axis, bin_number=10):

    all_histo_mouse = np.zeros((len(json_mouse_raw_data.keys())-1, bin_number))
    all_histo_bbox_max = np.zeros((len(json_mouse_raw_data.keys())-1, bin_number))
    all_histo_bbox_min = np.zeros((len(json_mouse_raw_data.keys())-1, bin_number))
    all_histo_headpose = np.zeros((len(json_mouse_raw_data.keys())-1, bin_number))

    mouse_count = 0
    bbox_max_count = 0
    bbox_min_count = 0
    headpose_count = 0

    idx = 0
    for (student_id_, i) in json_mouse_raw_data.items():
        # control no current student and no other question set
        if student_id_ == student_id or student_id_[-1] != student_id[-1] or student_id in abandon_student_list:
            continue
        try:
            histo_mouse = np.histogram(pd.DataFrame.from_records(json_mouse_raw_data[student_id_][question_id])[f'screen{axis}_scaled'], range=(-1,1), bins=bin_number)[0]

            if np.sum(histo_mouse) == 0:
                all_histo_mouse[idx,:] = np.zeros_like(histo_mouse)
            else:    
                all_histo_mouse[idx,:] = histo_mouse/np.sum(histo_mouse)
                mouse_count += 1
        except:
            print(student_id_, question_id)
        
        try:
            histo_bbox_max = np.histogram(pd.DataFrame.from_records(json_bbox_raw_data[student_id_][question_id])[f'{axis}_max_scaled'], range=(-1,1), bins=bin_number)[0]
            # all_histo_bbox_max[idx,:] = histo_bbox_max/np.sum(histo_bbox_max)
            
            if np.sum(histo_bbox_max) == 0:
                all_histo_bbox_max[idx,:] = np.zeros_like(histo_bbox_max)
            else:    
                all_histo_bbox_max[idx,:] = histo_bbox_max/np.sum(histo_bbox_max)
                bbox_max_count += 1
        except:
            print(student_id_, question_id)
        
        try:
            histo_bbox_min = np.histogram(pd.DataFrame.from_records(json_bbox_raw_data[student_id_][question_id])[f'{axis}_min_scaled'], range=(-1,1), bins=bin_number)[0]
            # all_histo_bbox_min[idx,:] = histo_bbox_min/np.sum(histo_bbox_min)
            
            if np.sum(histo_bbox_min) == 0:
                all_histo_bbox_min[idx,:] = np.zeros_like(histo_bbox_min)
            else:    
                all_histo_bbox_min[idx,:] = histo_bbox_min/np.sum(histo_bbox_min)
                bbox_min_count += 1

        except:
            print(student_id_, question_id)
        
        try:
            if axis == 'X':
                histo_headpose = np.histogram(pd.DataFrame.from_records(json_headpose_raw_data[student_id_][question_id])[f'yaw_scaled'], range=(-1,1), bins=bin_number)[0]
            else:
                histo_headpose = np.histogram(pd.DataFrame.from_records(json_headpose_raw_data[student_id_][question_id])[f'pitch_scaled'], range=(-1,1), bins=bin_number)[0]

            if np.sum(histo_headpose) == 0:
                all_histo_headpose[idx,:] = np.zeros_like(histo_headpose)
            else:    
                all_histo_headpose[idx,:] = histo_headpose/np.sum(histo_headpose)
                headpose_count += 1
            # all_histo_headpose[idx,:] = histo_headpose/np.sum(histo_headpose)
        except:
            print(student_id_, question_id)
        
        idx+=1

    return {
        "mouse": (np.sum(all_histo_mouse, 0)/mouse_count).tolist(),
        "bbox_max": (np.sum(all_histo_bbox_max, 0)/bbox_max_count).tolist(),
        "bbox_min": (np.sum(all_histo_bbox_min, 0)/bbox_min_count).tolist(),
        "headpose": (np.sum(all_histo_headpose, 0)/headpose_count).tolist()
    }

# optional parameters: question_id, threshold of z_score on headpose abnormal detection, instance or number of cases
# example: /api/student_suspicious_case/dong_A1?question_id=mc_1&threshold=1&instance=1
@app.route("/api/student_suspicious_case/<string:student_id>/", methods=['POST','GET'])
def student_suspicious_case(student_id):
    question_id = request.args.get('question_id', type=str, default=None)
    headpose_z_score_threshold = float(request.args.get('threshold', type=str, default=3.0))
    instance = request.args.get('instance', type=int, default=1)

    if question_id == None:
        dict_all_suspicious_cases = {}
        for question_id_ in ['mc_1', 'mc_2', 'mc_3', 'mc_4', 'mc_5', 'mc_6', 'mc_7', 'mc_8', 'mc_9', 'mc_10', 'sa_1', 'sa_2','sa_3', 'sa_4']:
            dict_temp = {}
            # df_headpose = pd.DataFrame.from_records(json_bbox_raw_data[student_id][question_id_])
            try:
                dict_temp['headpose'] = _.filter(json_headpose_raw_data[student_id][question_id_], lambda x: abs(x['yaw_z_score'])>=headpose_z_score_threshold or abs(x['pitch_z_score'])>=headpose_z_score_threshold)
            except:
                dict_temp['headpose'] = []
            try:
                dict_temp['blur_focus'] = _.filter(json_mouse_special_event[student_id][question_id_], lambda x: x['type'] == 'blur' or x['type'] == 'focus')
            except:
                dict_temp['blur_focus'] = []
            try:
                dict_temp['copy_paste'] = _.filter(json_mouse_special_event[student_id][question_id_], lambda x: x['type'] == 'copy' or x['type'] == 'paste')
            except:
                dict_temp['copy_paste'] = []
            # dict_temp['contextmenu'] = _.filter(json_mouse_special_event[student_id][question_id_], lambda x: x['type'] == 'contextmenu')
            try:
                dict_temp['no_face'] = _.filter(json_bbox_raw_data[student_id][question_id_], lambda x: x['no_face'] == 1)
            except:
                dict_temp['no_face'] = []

            if instance == 0:
                dict_temp_no_instance = {}
                for (k, v) in dict_temp.items():
                    dict_temp_no_instance[k] = len(v)
                dict_temp_no_instance['question_id'] = question_id_
                dict_all_suspicious_cases[question_id_] = dict_temp_no_instance
            else:
                dict_all_suspicious_cases[question_id_] = dict_temp

        return dict_all_suspicious_cases
    
    else:
        dict_single_suspicious_case = {}
        dict_single_suspicious_case['headpose'] = _.filter(json_headpose_raw_data[student_id][question_id], lambda x: abs(x['yaw_z_score'])>=headpose_z_score_threshold or abs(x['pitch_z_score'])>=headpose_z_score_threshold)
        dict_single_suspicious_case['blur_focus'] = _.filter(json_mouse_special_event[student_id][question_id], lambda x: x['type'] == 'blur' or x['type'] == 'focus')
        dict_single_suspicious_case['copy_paste'] = _.filter(json_mouse_special_event[student_id][question_id], lambda x: x['type'] == 'copy' or x['type'] == 'paste')
        dict_single_suspicious_case['contextmenu'] = _.filter(json_mouse_special_event[student_id][question_id], lambda x: x['type'] == 'contextmenu')
        dict_single_suspicious_case['no_face'] = _.filter(json_bbox_raw_data[student_id][question_id], lambda x: x['no_face'] == 1)

        if instance == 0:
            dict_single_suspicious_case_no_instance = {}
            for (k, v) in dict_single_suspicious_case.items():
                dict_single_suspicious_case_no_instance[k] = len(v)
            dict_single_suspicious_case_no_instance['question_id'] = question_id
            return dict_single_suspicious_case_no_instance
        else:
            return dict_single_suspicious_case

# level-> overall or question_level; question_set: A or B; threshold: the same as student_suspicious_case
@app.route("/api/overall_suspicious_case/<string:level>/<string:question_set>/<threshold>", methods=['POST','GET'])
@app.route("/api/overall_suspicious_case/<string:level>/<string:question_set>", methods=['POST','GET'])
def overall_suspicious_case(level, question_set, threshold=2.0):
    # Shape of (student, question, type)
    all_suspicious_cases = []

    threshold = float(threshold)

    list_question_id = ['mc_1', 'mc_2', 'mc_3', 'mc_4', 'mc_5', 'mc_6', 'mc_7', 'mc_8', 'mc_9', 'mc_10', 'sa_1', 'sa_2','sa_3', 'sa_4']
    # list_cheating = ["blur_focus", "copy_paste", "contextmenu", "headpose", "no_face"]
    list_cheating = ["blur_focus", "copy_paste", "headpose", "no_face"]

    for student_id in json_mouse_raw_data.keys():
        list_blur_focus = []
        list_copy_paste = []
        # list_contextmenu = []
        list_headpose = []
        list_no_face = []
        if student_id[-1] != question_set or student_id in abandon_student_list:
            continue
        for question_id in list_question_id:
            try:
                list_blur_focus.append(len(_.filter(json_mouse_special_event[student_id][question_id], lambda x: x['type'] == 'blur' or x['type'] == 'focus')))
            except:
                list_blur_focus.append(0)
            try:  
                list_copy_paste.append(len(_.filter(json_mouse_special_event[student_id][question_id], lambda x: x['type'] == 'copy' or x['type'] == 'paste')))
            except:
                list_copy_paste.append(0)
            # try:      
            #     list_contextmenu.append(len(_.filter(json_mouse_special_event[student_id][question_id], lambda x: x['type'] == 'contextmenu')))
            # except:
            #     list_contextmenu.append(0)
            try:     
                list_headpose.append(len(_.filter(json_headpose_raw_data[student_id][question_id], lambda x: abs(x['yaw_z_score'])>=threshold or abs(x['pitch_z_score'])>=threshold)))
            except:
                list_headpose.append(0)
            try:      
                list_no_face.append(len(_.filter(json_bbox_raw_data[student_id][question_id], lambda x: x['no_face'] == 1)))
            except:
                list_no_face.append(0)

        # array_question = np.array([list_blur_focus, list_copy_paste, list_contextmenu, list_headpose, list_no_face])
        array_question = np.array([list_blur_focus, list_copy_paste, list_headpose, list_no_face])
        all_suspicious_cases.append(array_question)

    array_all_suspicious_cases = np.stack(all_suspicious_cases)

    if level == 'question':
        quantile_25 = np.quantile(array_all_suspicious_cases, 0.25, axis=0)
        quantile_75 = np.quantile(array_all_suspicious_cases, 0.75, axis=0)
        median = np.median(array_all_suspicious_cases, axis=0)
        mean = np.mean(array_all_suspicious_cases, axis=0)
        max_ = np.max(array_all_suspicious_cases, axis=0)
        min_ = np.min(array_all_suspicious_cases, axis=0)

        dict_result = {}
        for i in range(len(list_question_id)):
            dict_temp = {}
            for j in range(len(list_cheating)):
                dict_stat = {}
                dict_stat['quantile_25'] = quantile_25[j, i]
                dict_stat['quantile_75'] = quantile_75[j, i]
                dict_stat['median'] = median[j, i]
                dict_stat['mean'] = mean[j, i]
                dict_stat['max'] = int(max_[j, i])
                dict_stat['min'] = int(min_[j, i])
                dict_temp[list_cheating[j]] = dict_stat
            dict_result[list_question_id[i]] = dict_temp

        return dict_result
    else:
        quantile_25 = np.quantile(np.sum(array_all_suspicious_cases, axis=2), 0.25, axis=0)
        quantile_75 = np.quantile(np.sum(array_all_suspicious_cases, axis=2), 0.75, axis=0)
        median = np.median(np.sum(array_all_suspicious_cases, axis=2), axis=0)
        mean = np.mean(np.sum(array_all_suspicious_cases, axis=2), axis=0)
        max_ = np.max(np.sum(array_all_suspicious_cases, axis=2), axis=0)
        min_ = np.min(np.sum(array_all_suspicious_cases, axis=2), axis=0)

        print(np.sum(array_all_suspicious_cases, axis=2))
        print(array_all_suspicious_cases.shape)
        
        dict_result = {}
        for j in range(len(list_cheating)):
            dict_stat = {}
            dict_stat['quantile_25'] = quantile_25[j]
            dict_stat['quantile_75'] = quantile_75[j]
            dict_stat['median'] = median[j]
            dict_stat['mean'] = mean[j]
            dict_stat['max'] = int(max_[j])
            dict_stat['min'] = int(min_[j])
            # print(dict_stat)
            dict_result[list_cheating[j]] = dict_stat

        return dict_result


    

  
