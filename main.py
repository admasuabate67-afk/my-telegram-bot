from PIL import Image

def process_digital_id(template_a_path, template_b_path, output_path):
    # 1. ቴምፕሌቶችን ይክፈቱ
    try:
        id_template_a = Image.open(template_a_path) # input ID
        new_template_b = Image.open(template_b_path) # empty new template
    except FileNotFoundError:
        print("ስህተት: የቴምፕሌት ፋይሎች አልተገኙም::")
        return

    # ------------------------------------------------------------------
    # Step 1: መረጃን ከ Template A ይቁረጡ (CROPPING)
    # ማሳሰቢያ፡ እነዚህ ቁጥሮች በሙከራ የተገኙ ትክክለኛ ቦታዎች ናቸው::
    # (left, top, right, bottom)
    # ------------------------------------------------------------------

    # ሀ. ፎቶውን መቁረጥ (ሳጥን 1 - ለፎቶው)
    photo_box = (325, 316, 786, 584)
    extracted_photo = id_template_a.crop(photo_box)

    # ለ. ስም መቁረጥ (ሳጥን 2 - ሙሉ ስም)
    name_box = (175, 608, 680, 660)
    extracted_name = id_template_a.crop(name_box)

    # ሐ. ጾታ መቁረጥ (ሳጥን 4 - ጾታ)
    sex_box = (175, 706, 680, 730)
    extracted_sex = id_template_a.crop(sex_box)

    # መ. የሚያበቃበት ቀን መቁረጥ (ሳጥን 5 - Expiry)
    expiry_box = (175, 740, 680, 770)
    extracted_expiry = id_template_a.crop(expiry_box)

    # ሠ. የካርድ ቁጥር/FAN (ሳጥን 6 - FAN)
    fan_box = (335, 777, 720, 836)
    extracted_fan = id_template_a.crop(fan_box)

    # ረ. የተሰጠበት ቀን መቁረጥ (ሳጥን 7 - Date of Issue)
    issue_box = (891, 336, 953, 700)
    extracted_issue = id_template_a.crop(issue_box)


    # ------------------------------------------------------------------
    # Step 2: የተቆረጠውን መረጃ Template B ላይ ያስገቡ (PASTING)
    # መጋጠሚያዎቹ (x, y) ለላይኛው ግራ ጫፍ ናቸው::
    # ------------------------------------------------------------------

    # ሀ. ፎቶውን መለጠፍ (አዲሱ ሳጥን 8 - "ፋይዳ" በታች)
    # በTemplate B ላይ "FAYDA/ፋይዳ" የሚለው ጽሑፍ በግምት y=600 ላይ ነው::
    # ፎቶው በ x=745, y=724 አካባቢ እንዲቀመጥ ተደርጓል::
    new_photo_position = (745, 724)
    new_template_b.paste(extracted_photo, new_photo_position)

    # ለ. ስም መለጠፍ
    new_name_position = (410, 290)
    new_template_b.paste(extracted_name, new_name_position)

    # ሐ. ጾታ መለጠፍ
    new_sex_position = (410, 560)
    new_template_b.paste(extracted_sex, new_sex_position)

    # መ. የሚያበቃበት ቀን መለጠፍ
    new_expiry_position = (410, 668)
    new_template_b.paste(extracted_expiry, new_expiry_position)

    # ሠ. የካርድ ቁጥር መለጠፍ
    new_fan_position = (465, 765)
    new_template_b.paste(extracted_fan, new_fan_position)

    # ረ. የተሰጠበት ቀን መለጠፍ
    # (በአዲስ ቴምፕሌት y-ዘንግ ላይ 90 ዲግሪ መሽከርከር ሊኖርበት ይችላል::)
    new_issue_position = (88, 160)
    new_template_b.paste(extracted_issue, new_issue_position)

    # ------------------------------------------------------------------
    # Step 3: የመጨረሻውን ውጤት ያስቀምጡ
    # ------------------------------------------------------------------
    new_template_b.save(output_path)
    print(f"ፋይሉ በተሳካ ሁኔታ ተፈጥሯል: {output_path}")

# ------------------------------------------------------------------
# አጠቃቀም (የፋይል ስሞችን እዚህ ይግለጹ)
# ------------------------------------------------------------------

# 'image_0.png' እና 'image_1.png' ከዚህ ኮድ ጋር በአንድ ፎልደር ውስጥ መሆን አለባቸው::
input_id_a = "image_0.png"
empty_template_b = "image_1.png"
final_id_output = "Final_Processed_ID.png"

# ተግባሩን ይጥሩ
process_digital_id(input_id_a, empty_template_b, final_id_output)
