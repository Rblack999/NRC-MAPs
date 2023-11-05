# hello=[1,2,'false']
# print(type(hello))
#
# try:
#     if not all(isinstance(i,int) for i in hello):
#         print('Name must be a list, currently is a ', type(hello))
#
# except Exception as e:
#     flag_read_params = 1
#     print(e)
#
# hello=["FALSE","False","false"]
#
#
# try:
#     if not all(isinstance(bool(i),bool) for i in hello):
#         print('Name must be a list, currently is a ', type(hello))
#
# except Exception as e:
#     flag_read_params = 1
#     print(e)

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


# param = False
# if not isinstance(param, float) and not isfloat(param):
#     print('bad')

hello=[1,2,'s']

for i in hello:
    print(isfloat(i))

if not all(isinstance(i,float) for i in hello) and not all(isfloat(i) for i in hello):
    print('Name must be a list, currently is a ', type(hello))

