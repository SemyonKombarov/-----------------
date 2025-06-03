from pyproj import Transformer

transformer = Transformer.from_crs(32642,4326)
file = open("coords.txt", "r")

# print(content)

lst = []
while True:
    content = file.readline()
    if not content:
        break
    lst.append(content.split())
print(lst)
file.close()

output = open("output.txt", "w+")
for i in lst:
    tmp = transformer.transform(i[1],i[0])
    output.write(str(tmp)+"\n")
    print(tmp)

 

output.close()