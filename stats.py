import matplotlib.pyplot as plt
import csv

p_save, p_load, p_size = [], [], []
ie_save, ie_load, ie_size = [], [], []
websites = [
    "Google",
    "Reddit",
    "WhatsApp",
    "Wikipedia",
    "Yahoo",
    "Yahoo JP",
    "Baidu",
    "Netflix",
    "LinkedIn",
    "Office",
    "Naver",
    "Yahoo News JP",
    "Twitch",
    "Samsung",
    "Globo",
    "Fandom",
    "Weather",
    "Telegram"
]

with open("data.csv") as f:
    reader = csv.reader(f)
    counter = 0
    for row in reader:
        counter += 1
        if counter == 1:
            continue
        p_save.append(float(row[0]))
        p_load.append(float(row[2]))
        p_size.append(float(row[4]))
        ie_save.append(float(row[5]))
        ie_load.append(float(row[7]))
        ie_size.append(float(row[9]))

plt.figure(figsize=(10, 10))
plt.plot(websites, p_save, "ro")
plt.plot(websites, ie_save, "bo")
plt.xticks(rotation=45)
plt.legend(["Permadiff", "IE Snapshot"])
plt.ylabel("Save Time (ms)")
plt.yscale("log")


for i in range(len(websites)):
    plt.plot([websites[i], websites[i]], [p_save[i], ie_save[i]], "k-")

plt.savefig("p_save_vs_ie_save.png", bbox_inches="tight")

plt.clf()

# do the same thing as above for load time

plt.figure(figsize=(10, 10))
plt.plot(websites, p_load, "ro")
plt.plot(websites, ie_load, "bo")
plt.xticks(rotation=45)
plt.legend(["Permadiff", "IE Snapshot"])
plt.ylabel("Load Time (ms)")
plt.yscale("log")

for i in range(len(websites)):
    plt.plot([websites[i], websites[i]], [p_load[i], ie_load[i]], "k-")

plt.savefig("p_load_vs_ie_load.png", bbox_inches="tight")

plt.clf()

# do the same thing as above for size

plt.figure(figsize=(20, 10))
plt.plot(websites, p_size, "ro")
plt.plot(websites, ie_size, "bo")
plt.xticks(rotation=45)
plt.legend(["Permadiff", "IE Snapshot"])
plt.ylabel("Size (kilobytes)")
plt.yscale("log")

for i in range(len(websites)):
    plt.plot([websites[i], websites[i]], [p_size[i], ie_size[i]], "k-")

plt.savefig("p_size_vs_ie_size.png", bbox_inches="tight")
