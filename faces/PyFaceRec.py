import cv2 as cv
import face_recognition
import os
import np
import copy
import webcolors
import CfgManager as cfg
from PIL import Image


# 读取设置
face_path = cfg.read_cfg('face_path')    # 人脸字典路径
camera = int(cfg.read_cfg('camera'))     # 默认启用摄像头

tolerance = float(cfg.read_cfg('tolerance'))     # 契合度阈值
border_color = webcolors.name_to_rgb(cfg.read_cfg('border_color'))    # 人脸边框颜色
border_thickness = int(cfg.read_cfg('border_thickness'))    # 边框厚度
is_performance_mode = cfg.read_cfg('is_performance_mode')    # 是否启用性能模式

# 全局变量
known_face_names = []


def jpeg2jpg(path_in, path_out):
    # jpeg转jpg
    img = Image.open(path_in)
    img.save(path_out, "JPEG", quality=80, optimize=True, progressive=True)


def read_directory(directory_name):
    # 读取指定目录中的所有图片并返回图片列表
    array_of_img = []
    for filename in os.listdir(r"./" + directory_name):
        img = cv.imread(directory_name + "/" + filename)
        array_of_img.append(img)
        known_face_names.append(os.path.splitext(filename)[0])
    return array_of_img


def do_encoding(img_array):
    # 对传入列表中的所有图片进行编码
    known_face_encodings = []
    for img in img_array:
        count = 0
        face_locaion = face_recognition.face_locations(img)
        if len(face_locaion) == 1:
            face_encoding = face_recognition.face_encodings(img, num_jitters=2)[0]
            known_face_encodings.append(face_encoding)
        elif len(face_locaion) == 0:
            print(known_face_names[count]+' no face included')
        count += 1
    return known_face_encodings


def show_menu():
    print('\033[1;32m==============================Function Menu==============================\033[0m')
    print('press 1 for : FaceRecognition')
    print('press 2 for : LoadNewFace')
    print('press 3 for : ShowSettingTree')
    print('press 4 for : ChangeSettings')
    print('press 5 for : Exit')
    key = input('\033[4;33menter num and press enter : \033[0m')
    function_choose(key)


def function_choose(num):
    # 功能选择
    numbers = {
        '1': do_recognition,
        '2': load_new_face,
        '3': show_tree,
        '4': change_settings,
        '5': exit_pyface,
    }

    numbers.get(num, default)()


def default():
    print('\033[1;31mError:no such function\033[0m')
    key = input('\033[4;33mpress num and press enter :\033[0m')
    function_choose(key)


def do_recognition():
    print('\033[1;33m==============================loading face img==============================\033[0m')
    array_of_img = read_directory(face_path)
    print('%d loaded pictures' % len(array_of_img))
    for n in known_face_names:
        print(n)
    print('\033[1;31m--Finished--\033[0m')

    print('\033[1;33m=============================encoding known face=============================\033[0m')
    print('tips: if there are too many face image, it might take a long time')
    print('\033[5;32mLoading now...\033[0m')
    known_face_encodings = do_encoding(array_of_img)
    if len(known_face_encodings) == 0:
        print("\033[1;31mERROR: no face included please load one frist\033[0m")
        show_menu()
        return
    print("\033[1;31m--Finished--\033[0m")
    process_this_frame = True
    capture = cv.VideoCapture(camera, cv.CAP_DSHOW)
    print('\033[1;33m===========================face recognition start=============================\033[0m')
    print("\033[1;36mpress 'q' exit\033[0m")

    # 判断是否处于性能模式
    # if y resizeframe
    _fx = 1
    _fy = 1
    if is_performance_mode == 'True':
        _fx = 0.25
        _fy = 0.25
    while 1:
        ret, frame = capture.read()
        if ret is False:
            break
        small_frame = cv.resize(frame, (0, 0), fx=_fx, fy=_fy)
        # 转BGR图像
        rgb_small_frame = small_frame[:, :, ::-1]
        if process_this_frame:
            # 调用face_recognition获取人脸位置
            unknown_face_locations = face_recognition.face_locations(rgb_small_frame)
            # 对未知图像进行编码
            unknown_face_encodings = face_recognition.face_encodings(rgb_small_frame, unknown_face_locations)
            # 识别人脸
            face_names = []
            for unknown_face_encoding in unknown_face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding, tolerance)
                name = "Unknown"
                face_distances = face_recognition.face_distance(known_face_encodings, unknown_face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame

        # 在图像中显示姓名
        for (top, right, bottom, left), name in zip(unknown_face_locations, face_names):
            # 转换真实尺寸坐标
            if is_performance_mode == 'True':
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

            # Draw a box around the face
            cv.rectangle(frame, (left, top), (right, bottom), border_color, border_thickness)

            # Draw a label with a name below the face
            cv.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv.FILLED)
            font = cv.FONT_HERSHEY_DUPLEX
            cv.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv.imshow("face", frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyWindow('face')
            capture.release()
            break

    main()


def load_new_face():
    print('\033[1;33m==============================Add New Face==============================\033[0m')
    print("\033[1;36mpress 's' take a shot\033[0m")
    print("\033[1;31mpress 'q' to exit\033[0m")
    capture = cv.VideoCapture(camera, cv.CAP_DSHOW)
    while 1:
        ret, frame = capture.read()
        if ret is False:
            break
        rgb_frame = frame[:, :, ::-1]
        frame_copy = copy.copy(frame)
        face_location = face_recognition.face_locations(rgb_frame)

        for (top, right, bottom, left) in face_location:
            # Draw a box around the face
            cv.rectangle(frame_copy, (left, top), (right, bottom), (0, 255, 0), 2)
        cv.imshow('capture', frame_copy)

        pressed_key = cv.waitKey(1) & 0xFF
        # 在正确的时机触发提示
        if pressed_key == ord('s') and len(face_location) == 1:
            name = input('please enter your name :')

            # 使用自适应直方图均衡化
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl1 = clahe.apply(gray)
            cv.imwrite("./Facedirectory/%s.jpeg" % name, cl1)
            print('\033[1;31m--Finished--\033[0m')
            source = './Facedirectory./' + str(name) + '.jpeg'
            target = './Facedirectory./' + str(name) + '.jpg'
            jpeg2jpg(source, target)
            os.remove('./Facedirectory./' + str(name) + '.jpeg')
            key = input('\033[4;33mwould you like to add another face? (y/n): \033[0m')
            if key == 'n':
                break
            elif key == 'y':
                print("\033[1;36mpress 's' take a shot\033[0m")
                print("\033[1;31mpress 'q' to exit\033[0m")
                continue

        elif pressed_key == ord('s') and len(face_location) == 0:
            print('No face detected')
        elif pressed_key == ord('s') and len(face_location) > 1:
            print('Make sure there is only one face in the image')
        elif pressed_key == ord('q'):
            break

    cv.destroyWindow('capture')
    capture.release()
    main()


def show_tree():
    cfg.show_cfgtree()
    print('\033[1;31m--Finished--\033[0m')
    main()


def change_settings():
    cfg.change_cfg()
    print('\033[1;31m--Finished--\033[0m')
    main()


def exit_pyface():
    cv.destroyAllWindows()


def main():
    show_menu()


if __name__ == '__main__':
    main()
