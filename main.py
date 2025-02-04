from os import system as sys
from os import remove as rm
from os import path


def parse_response(resp):
    lines = resp.split('\n')
    return lines[8] + lines[10]

def  main():
    sys("chcp 65001")
    list_of_resorces = ['google.com', 'yandex.ru', 'random.org', 'chess.com', 'youtube.com']

    if path.exists("answer.csv"):
        rm("answer.csv")
    file = open("answer.csv", "a",encoding='utf8')

    res_lines = []

    for res in list_of_resorces:
        answer = sys(f'ping {res} > {res}',)
        if answer == 0:
            with open(res, "r") as f:
                res_lines.append(f"{res};\"{parse_response(f.read())}\";")
        else:
            print("Something went wrong")
    
    file.write('\n'.join(res_lines))
    file.close()
    for res in list_of_resorces:
        rm(res)

if __name__ == "__main__":
    main()