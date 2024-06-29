import json
import random
from pathlib import Path
import numpy as np

def rand_weight(s):
    bracket_type = random.choice(['[]', '{}'])
    bracket_num = random.randint(0, 4)
    if bracket_type == '[]':
        s = '[' * bracket_num + s + ']' * bracket_num
    else:
        s = '{' * bracket_num + s + '}' * bracket_num
    return s

def rand_style_(content):
    with open(Path(__file__).parent / "tags1.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        t = []
        artists_plain = map(str, random.sample(data["artist"], random.randint(5, 7)))
        artists_decorated = map(rand_weight, artists_plain)
        t.append(','.join(artists_decorated))
        t.append(content)
        t.append("best quality, amazing quality, very aesthetic, absurdres")
        tags =  ','.join(filter(None, t))
        return tags
    
def rand_character_(content):
    with open(Path(__file__).parent / "tags.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        t = []
        if content == "" or content is None:
            t.append("".join(map(str, random.sample(data["character"], random.randint(1, 1)))))
        else:
            t.append(content)
        
        artists_plain = map(str, random.sample(data["artist"], random.randint(5, 7)))
        artists_decorated = map(rand_weight, artists_plain)
        t.append(','.join(artists_decorated))
        t.append(','.join(map(str, random.sample(data["camera"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        group_prob = 0.9    # 80% 概率选择分支组
        branch1_prob = 0.85  # 60% 概率选择分支1
        rand_num = random.random()
        if rand_num < group_prob:
            rand_num = random.random()
            if rand_num < branch1_prob:
                t.append(','.join(map(str, random.sample(data["environment_background"]["environment"], random.randint(0,1)))))
            else:
                t.append(','.join(map(str, random.sample(data["environment_background"]["background"], random.randint(1,1)))))

        t.append(','.join(map(str, random.sample(data["shadow"], random.choices([0, 1], weights=[0.8, 0.2], k=1)[0]))))
        t.append("1girl,solo")

        branch = ['b1', 'b2', 'b3']
        selected_tag = random.choice(branch)
        if selected_tag == 'b1':
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["hair_ornaments"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["nechlace"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["cloth"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["sleeves"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["underwear"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["pants"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["panties"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["legwear"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["socks"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["hats"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["facial_accessories"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["earring"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["hand_ornaments"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["clothing_decoration"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["shoes"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["clothing"]["suits_1"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'b2':
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["R18"]["R18_clothing"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["R18"]["legwear"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["R18"]["panties"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["R18"]["underwear"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["R18"]["socks"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        else:
            t.append(','.join(map(str, random.sample(data["clothing_suits_R18"]["suits"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))


        t.append(','.join(map(str, random.sample(data["hair"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        t.append(','.join(map(str, random.sample(data["face"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        t.append(','.join(map(str, random.sample(data["sight"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        t.append(','.join(map(str, random.sample(data["expression"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))

        tags = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6']
        probs = [0.2, 0.1, 0.1, 0.2, 0.2, 0.2]
        selected_tag = np.random.choice(tags, p=probs)
        if selected_tag == 'tag1':
            t.append(','.join(map(str, random.sample(data["action_1"]["interaction"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag2':
            t.append(','.join(map(str, random.sample(data["action_1"]["physical_exercise"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag3':
            t.append(','.join(map(str, random.sample(data["action_1"]["integral_action"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag4':
            t.append(','.join(map(str, random.sample(data["action_1"]["sitting"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        elif selected_tag == 'tag5':
            t.append(','.join(map(str, random.sample(data["action_1"]["standing"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        else:
            t.append(','.join(map(str, random.sample(data["action_1"]["leg_posture"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))

        t.append(','.join(map(str, random.sample(data["head_movements"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        t.append(','.join(map(str, random.sample(data["chest"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        t.append(','.join(map(str, random.sample(data["lean"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))

        tags = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5']
        probs = [0.1, 0.1, 0.8/3, 0.8/3, 0.8/3]
        selected_tag = np.random.choice(tags, p=probs)
        if selected_tag == 'tag1':
            t.append(','.join(map(str, random.sample(data["action_2"]["run_one's_hair"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag2':
            t.append(','.join(map(str, random.sample(data["action_2"]["hand_position"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag3':
            t.append(','.join(map(str, random.sample(data["action_2"]["holding"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        elif selected_tag == 'tag4':
            t.append(','.join(map(str, random.sample(data["action_2"]["gesture"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        elif selected_tag == 'tag5':
            t.append(','.join(map(str, random.sample(data["action_2"]["undress"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))
        t.append(','.join(map(str, random.sample(data["general_item"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))

        tags = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5']
        probs = [0.1, 0.1, 0.1, 0.1, 0.6]
        selected_tag = np.random.choice(tags, p=probs)
        if selected_tag == 'tag1':
            t.append(','.join(map(str, random.sample(data["theme_item"]["recreation_and_sports"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag2':
            t.append(','.join(map(str, random.sample(data["theme_item"]["weapons_and_tools"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag3':
            t.append(','.join(map(str, random.sample(data["theme_item"]["animal"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag4':
            t.append(','.join(map(str, random.sample(data["theme_item"]["plant"], random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]))))
        elif selected_tag == 'tag5':
            t.append(','.join(map(str, random.sample(data["theme_item"]["food"], random.choices([0, 1], weights=[0.1, 0.9], k=1)[0]))))

        t.append("best quality, amazing quality, very aesthetic, absurdres")
        tags =  ','.join(filter(None, t))
        return tags