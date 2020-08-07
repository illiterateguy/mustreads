import csv

from model import *

def main():
    f = open("books.csv") 
    reader = csv.reader(f)
    for isbn,title,author,year in reader:
        db.execute("INSERT INTO books(isbn,title,author,year) VALUES(:isbn,:title,:author,:year)",
        {"isbn" : isbn ,"title" : title,"author" : author,"year":year})
    db.commit()    
        

if __name__ == "__main__":
    main()