import requests
import queue
# url
url = "http://ids.sensetime.com"
# # token
# auth_token = "2d53d66a103faa6d66a780deb5e88c0ae1d3c450"
# headers = {"Authorization": f"Token {auth_token}"}
# # 运营码
# lbs_operations_code = "AUTOTASK_BJ"
# # 场景码
# route_planning_scene_code = "ROUTE_PLANNING_TASK"
# token
auth_token = "6b43fc86f27774781da03b38b26c4494e651358d"
headers = {"Authorization": f"Token {auth_token}"}
# 运营码
lbs_operations_code='UBOX_SZ'
# 场景码
route_planning_scene_code = "UBOX_REALTIME"
loc_uuid_all = []
address_arr = []
# uuid
uuid_all = []
# 经纬度
coordinate_all = []
coordinate_test = []
address_01 = []
final_result_all = ""

class IDS:
    def __init__(self, q_response, summarize):
        self.name = "ids"
        self.description = ""
        self.q_response = q_response
        self.summarize = summarize

    # 地址转换为经纬度
    def get_coordinate(self, address):
        address_01.append(address)
        global address_arr
        address_arr.append(address)
        url_location = url + '/api/v1.0/lbs_geocode_address'
        body_location = {
            "lbs_operations_code": lbs_operations_code,
            "address": address
        }
        # r 为响应对象
        r = requests.post(url_location, data=body_location, headers=headers, verify=False)
        # 查看响应结果
        location = r.json()['geocodes'][0]['location']
        # print(address_arr)
        # print(address + "的经纬度坐标为： " + str(location))
        global final_result_all
        final_result_all = address + "的经纬度坐标为： " + str(location)
        # print(final_result_all)
        # if not self.q_response is None:
        self.summarize.put(final_result_all)
        self.q_response.put(location)
        # 经纬度
        global coordinate_all
        coordinate_all.append(location)
        return location

    # 经纬度转换为IDS地理位置注册编码
    def get_uuid(self, coordinate):
        url_uuid = url + '/api/v1.0/lbs_location_register'
        body_uuid = {
            # "auth_token": auth_token,
            "lbs_operations_code": lbs_operations_code,
            "lon_lat": coordinate
        }
        # r为响应对象
        r = requests.post(url_uuid, data=body_uuid, headers=headers, verify=False)
        # 查看响应结果
        # print("api: " + str(r.json()))
        loc_uuid = r.json()['loc']['loc_uuid']
        global uuid_all
        uuid_all.append(loc_uuid)
        global coordinate_test
        coordinate_test.append(coordinate)
        # final_result = "该路口的周期设置为" + str(c) + "s比较合适。"
        # if not self.q_response is None:
        #     self.q_response.put(final_result)
        global final_result_all
        final_result_all = "经纬度坐标是"+coordinate+"的IDS地理位置注册编码为： " + str(loc_uuid)
        # print(final_result_all)
        # print(loc_uuid)
        # if not self.q_response is None:
        # final_result_all = ""
        self.summarize.put(final_result_all)
        self.q_response.put(loc_uuid)
        return loc_uuid

    # 路径规划实时查询
    def get_route_result(self, loc_uuid_all):

        url_route = url + "/api/v1.0/route_planning_realtime"
        body_route = {
            # "auth_token": auth_token,
            "lbs_operations_code": lbs_operations_code,
            "route_planning_scene_code": route_planning_scene_code,
            "uuid_list": loc_uuid_all
        }
        # r 为响应对象
        r = requests.post(url_route, data=body_route, headers=headers, verify=False)
        # 查看响应结果
        # print("api: " + str(r.json()))
        route_result = r.json()['route_result']
        # 规划的最终结果
        road = ""
        if len(address_arr) < len(loc_uuid_all):
            address_arr.append(loc_uuid_all[0])
            for i in route_result:
                if coordinate_all.index(coordinate_test[uuid_all.index(loc_uuid_all[i])]) != -1 :
                    test = address_arr[coordinate_all.index(coordinate_test[uuid_all.index(loc_uuid_all[i])])]
                else:
                    test = loc_uuid_all[i]
                road = road + str(test) + " -> "
        else:
            for i in route_result:

                road = road + address_arr[i] + " -> "
        # road = "规划的路径为：" + road[:-4]
        # if not self.q_response is None:
        road_summarize = "规划的路径为：" + road[:-4]
        road = len(loc_uuid_all)
        self.summarize.put(road_summarize)
        self.q_response.put(road)

        return road
    
    # 查询POI信息，通过关键字进行搜索
    def get_poi_search(self, keyword):
        name_all = []
        url_01 = url + '/api/v1.0/lbs_poi_search'
        body_01 = {
            # "auth_token": auth_token,
            "lbs_operations_code": lbs_operations_code,
            "keyword": keyword # 查询关键字:[多个关键字用“|”分割，若不指定 city，并且搜索的为泛词（例如“美食”）的情况下，返回的内容为城市列表以及此城市内有多少结果符合要求。]
        }
        # r 为响应对象
        r = requests.post(url_01, data=body_01, headers=headers, verify=False)
        # 查看响应结果
        # print(r.json())
        pois = r.json()['pois']
        for name in pois:
            name_all.append(name['name'])
        global final_result_all
        name_summarize = keyword + "包含" + "、".join(name_all)
        final_result_all = name_summarize
        # if not self.q_response is None:
        name_summarize = keyword + "搜索成功"
        name = "搜索成功"
        self.summarize.put(name_summarize)
        self.q_response.put(name)
        # print(self.name)
        return name

    # 查询IDS地理位置注册编码对应的经纬度坐标
    def get_location_search(self, uuid):
        # address_arr.append(uuid)
        url_02 = url + '/api/v1.0/lbs_location_search'
        body_02 = {
            # "auth_token": auth_token,
            "lbs_operations_code": lbs_operations_code,
            "uuid": uuid # 需要查询的IDS地理位置注册编码
        }
        # r 为响应对象
        r = requests.post(url_02, data=body_02, headers=headers, verify=False)
        # 查看响应结果
        # print(r.json())

        lon_lat = r.json()['locs'][0]['lon_lat']
        final_result_all = "IDS地理位置注册编码为" + uuid + "的经纬度坐标为： " + str(lon_lat)
        # self.q_response.put(lon_lat)
        self.summarize.put(final_result_all)
        self.q_response.put(lon_lat)
        coordinate_all.append(lon_lat)
        return lon_lat

    # 删除IDS地理位置注册编码对应的信息
    def get_location_delete(self, uuid):
        url_03 = url + "/api/v1.0/lbs_location_delete"
        body_03 = {
            # "auth_token": auth_token,
            "lbs_operations_code": lbs_operations_code,
            "uuid": uuid # 需要删除的IDS地理位置注册编码
        }
        # r 为响应对象
        r = requests.post(url_03, data=body_03, headers=headers, verify=False)
        # 查看响应结果
        # print(r.json())
        msg_code = r.json()['msg_code'] # 返回状态说明
        return msg_code

# q = queue.Queue()
# ids_func = IDS(q)
#
# code = "coordinate_01=ids_func.get_coordinate(address='广东省深圳市福田区福中三路市民中心C区')"
#
# exec(code)