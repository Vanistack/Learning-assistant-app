import json
import os

def merge_into_main_topics(auto_path="new_topics.json", main_path="topics.json"):
    if not os.path.exists(auto_path):
        print("No new topics to merge.")
        return

    with open(auto_path, "r") as f:
        new_topics = json.load(f)

    if not new_topics:
        print("✅ No new topics found to merge.")
        return

    if os.path.exists(main_path):
        with open(main_path, "r") as f:
            main_topics = json.load(f)
    else:
        main_topics = {}

    main_topics.update(new_topics)

    with open(main_path, "w") as f:
        json.dump(main_topics, f, indent=2)

    with open(auto_path, "w") as f:
        json.dump({}, f)

    print(f"✅ Merged {len(new_topics)} topics into {main_path}")

if __name__ == "__main__":
    merge_into_main_topics()
