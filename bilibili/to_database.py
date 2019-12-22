import psycopg2
import xlrd
# 利用psycopg2 实现python与PostgreSQL的交互

# 连接数据库，对应端口，数据框，用户，密码
def connect_db():
    conn = psycopg2.connect(database="bilivili",user="xiaolong",password="123456",host="127.0.0.1",port=5432)
    return conn
# 提交事务，保持持久化，关闭数据库
def close_db_connection(conn):
    conn.commit()
    conn.close()
# 在已创建的数据库下建立表，表分为视频信息和ｕｐ主信息
def create_db():
    conn = connect_db()
    if not conn:
        return
    # 获取操作数据库的接口
    cur = conn.cursor()
    # 创建Up_Info表，主键为ｕｐ的ｉｄ
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Up_Info(up_id VARCHAR(100) PRIMARY KEY, up_video_num integer, up_follow_num integer, up_like_num integer, up_playback_num integer)")
    # 创建video表,确认字段数据结构,主键为视频id,外键为up主id
    cur.execute(""" CREATE TABLE IF NOT EXISTS Video(video_aid VARCHAR(100) PRIMARY KEY, video_url VARCHAR(100),up_id VARCHAR(100) REFERENCES Up_Info(up_id), up_user_name VARCHAR(100), video_name VARCHAR(100), 
                video_published_at timestamp(8), video_playback_num integer, video_barrage_num integer, video_like_num integer, video_coin_num integer,
                video_favorite_num integer, video_forward_num integer, video_tag VARCHAR(100), video_length interval, created_at timestamp(8))""")
    close_db_connection(conn)

# 通过已有的excel表通过xlrd作为数据源进行读取
def init_db(excel_name):
    conn = connect_db()
    cur = conn.cursor()
    book = xlrd.open_workbook(excel_name)
    sheet1 = book.sheets()[0]
    sheet2 = book.sheets()[1]
    for row in range(1,sheet2.nrows):
        row_values = sheet2.row_values(row)
        # 嵌入sql,用%s作为占位符
        cur.execute("INSERT INTO Up_Info Values(%s, %s, %s, %s, %s)", (row_values[0],row_values[1],row_values[2],row_values[3],row_values[4]))
    for row in range(1,sheet1.nrows):
        row_values = sheet1.row_values(row)
        cur.execute("INSERT INTO Video Values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (row_values[0],row_values[1],row_values[2],row_values[3],row_values[4],row_values[5],row_values[6],row_values[7],row_values[8],row_values[9],row_values[10],row_values[11],row_values[12],row_values[13],row_values[14]))
    close_db_connection(conn)

# 调用函数进行工作
if __name__ == "__main__":
    create_db()
    init_db("test.xlsx")
    query_db()
