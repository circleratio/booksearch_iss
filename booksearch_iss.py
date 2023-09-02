#!/usr/bin/python3
import requests
import urllib
import xml.etree.ElementTree as et
import sys

class BookItem:
    def __init__(self, title, author, asin, isbn, published, series):
        self.title = title
        self.author = author
        self.asin = asin
        self.isbn = isbn
        self.published = published
        self.series = series

    def print(self):
        print('[{}({})]({})'.format(self.title, self.author, self.asin))
        print(f'ISBN: {self.isbn}')
        print(f'出版: {self.published}')
        print(f'シリーズ: {self.series}')

def print_book_list(book_list):
    for bi in book_list:
        bi.print()
        print()
        
def isbn2asin(isbn):
    if len(isbn) != 13:
        return(isbn)

    isbn = isbn[3:12]
    mult = 10
    check_digit = 0
    for c in list(isbn):
        check_digit += int(c) * mult
        mult -= 1
    check_digit = 11 - (check_digit % 11)
    if check_digit == 10:
        cs_s = 'X'
    else:
        cs_s =  str(check_digit)

    return(isbn + cs_s)

def search_ndl(title):
    title = sys.argv[1]
    title_enc = urllib.parse.quote(title)
    url = f'https://iss.ndl.go.jp/api/opensearch?title={title_enc}'
    res = requests.get(url)

    return (res.text)

def parse_xml_as_booklist(xml_text):
    book_list = []
    isbn_list = []
    root = et.fromstring(xml_text)
    channel = root.find('channel')

    for child in channel:
        isbn = ''
        if child.tag != 'item':
            continue
        if child.find('category') == None:
            continue
        elif child.find('category').text != '本':
            continue
        
        t = child.find('title').text
        
        if child.find('author') != None:
            a = child.find('author').text
        else:
            a = ''
            
        if  child.find('{http://purl.org/dc/elements/1.1/}date') != None:
            d = child.find('{http://purl.org/dc/elements/1.1/}date').text
        else:
            d = ''
            
        s = child.find('{http://ndl.go.jp/dcndl/terms/}seriesTitle')
        if s != None:
            s = s.text
        else:
            s = ''
            
        c = child.findall('{http://purl.org/dc/elements/1.1/}identifier')
        for i in c:
            if i.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] == 'dcndl:ISBN':
                isbn = i.text
            if isbn in isbn_list:
                continue
            else:
                isbn_list.append(isbn)
        asin = isbn2asin(isbn)

        if asin == '':
            continue

        bi = BookItem(t, a, asin, isbn, d, s)
        book_list.append(bi)

    return(book_list)
    
def main():
    if len(sys.argv) < 2:
        print('Usage: booksearch.py boodname')
        exit(1)

    xt = search_ndl(sys.argv[1])
    bl = parse_xml_as_booklist(xt)
    print_book_list(bl)

if __name__ == "__main__":
    main()
