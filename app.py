#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
from flask import Flask, request

app = Flask(__name__)
conn_db = sqlite3.connect("app_database.db", check_same_thread=False)


@app.route('/category', methods=['GET'])
def get_category():
    if request.args.get("list_one"):
        try:
            category_id = int(request.args.get("list_one"))
        except ValueError:
            return "Required integer value for param 'list_one'", 400
        else:
            return top_products_of_category(category_id, 4), 200
    else:
        return all_categories(), 200


@app.route('/search', methods=['GET'])
def get_search():
    if request.args.get("product_name"):
        return product_search(request.args.get("product_name"), 9), 200
    else:
        return "Param 'product_name' needed", 400


def all_categories():
    c = conn_db.cursor()
    h = c.execute('SELECT id_category, name, image, description FROM category_table').fetchall()
    c.close()

    categories_dict = [{
        "id_category": ai[0],
        "name": ai[1],
        "image": ai[2],
        "description": ai[3],
    } for ai in h]

    res = json.dumps(categories_dict)

    return res


def top_products_of_category(category_id, result_limit):
    c = conn_db.cursor()
    h = c.execute('SELECT id_product, name, image, more_info, buy_link, description, position FROM product_table '
                  'INNER JOIN rel_category_product ON product_table.id_product = rel_category_product.product '
                  'WHERE rel_category_product.category = ? AND rel_category_product.position <= ?'
                  , (category_id, result_limit)).fetchall()
    c.close()

    products_dict = [{
        "id_product": ai[0],
        "name": ai[1],
        "image": ai[2],
        "more_info": ai[3],
        "buy_link": ai[4],
        "description": ai[5],
        "position": ai[6]
    } for ai in h]

    res = json.dumps({
        "product": products_dict,
        "facebook_template": fb_template_product(h)
    })

    return res


def product_search(name, result_limit):
    c = conn_db.cursor()
    h = c.execute('SELECT id_product, name, image, more_info, buy_link, description FROM product_table '
                  'WHERE name LIKE ? LIMIT ?'
                  , ('%' + name + '%', result_limit)).fetchall()
    c.close()

    products_dict = [{
        "id_product": ai[0],
        "name": ai[1],
        "image": ai[2],
        "more_info": ai[3],
        "buy_link": ai[4],
        "description": ai[5]
    } for ai in h]

    res = json.dumps({
        "product": products_dict,
        "facebook_template": fb_template_product(h)
    })

    return res


def fb_template_product(products):
    elements = [{
        "title": ai[1],
        "image_url": ai[2],
        "item_url": ai[3],
        "subtitle": ai[5],
        "buttons": [
            {
                "type": "web_url",
                "url": ai[3],
                "title": "More Info"
            },
            {
                "type": "element_share"
            },
            {
                "type": "web_url",
                "url": ai[4],
                "title": "Buy !"
            }
        ],
    } for ai in products]

    res = {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
        }
    }
    return res


def populate():

    c = conn_db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS category_table(id_category INTEGER PRIMARY KEY, name TEXT UNIQUE, '
              'image TEXT, description TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS product_table(id_product INTEGER PRIMARY KEY, name TEXT UNIQUE, '
              'image TEXT, description TEXT, more_info TEXT, buy_link TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rel_category_product(product INTEGER, category INTEGER, position INTEGER, '
              'FOREIGN KEY(product) REFERENCES product_table(id_product), '
              'FOREIGN KEY(category) REFERENCES category_table(id_category), '
              'UNIQUE(product, category) ON CONFLICT REPLACE, '
              'UNIQUE(category, position) ON CONFLICT REPLACE)')

    if not c.execute('SELECT COUNT(*) FROM category_table').fetchone()[0]:
        c.executemany('INSERT INTO category_table(name, image, description) VALUES (?, ?, ?)',
                      [
                          ('Mac', 'http://store.storeimages.cdn-apple.com/4662/as-images.apple.com/is/image/AppleInc/aos/published/images/i/co/icon/mac/icon-mac?wid=99&hei=115&fmt=png-alpha&qlt=95&.v=1473804699963', 'description0'),
                          ('iPad', 'http://store.storeimages.cdn-apple.com/4662/as-images.apple.com/is/image/AppleInc/aos/published/images/i/co/icon/ipad/icon-ipad-special-deals?wid=99&hei=115&fmt=png-alpha&qlt=95&.v=1473804700010', 'description1'),
                          ('iPhone', 'http://images.apple.com/v/iphone/home/t/images/home/familybrowser/iphone_comp_dark_large.svg', 'description3'),
                      ])
        c.executemany('INSERT INTO product_table(name, image, description, more_info, buy_link) VALUES (?, ?, ?, ?, ?)',
                      [
                          ('MacBook',
                           'http://images.apple.com/v/mac/compare/f/compare/images/product_macbook_opt_large.png',
                           'description0',
                           'http://www.apple.com/es/macbook/', 'http://www.apple.com/es/shop/buy-mac/macbook'),
                          ('MacBook Pro',
                           'http://images.apple.com/v/mac/compare/f/compare/images/product_macbook_pro_touchbar_13_large.png',
                           'description1',
                           'http://www.apple.com/es/macbook-pro/', 'http://www.apple.com/es/shop/buy-mac/macbook-pro'),
                          ('iMac',
                           'http://images.apple.com/v/mac/compare/f/compare/images/product_imac_retina_21_large.png',
                           'description2',
                           'http://www.apple.com/es/imac/', 'http://www.apple.com/es/shop/buy-mac/imac'),
                          ('Mac Pro',
                           'http://images.apple.com/v/mac/compare/f/compare/images/product_mac_pro_large.png',
                           'description3',
                           'http://www.apple.com/es/mac-pro/', 'http://www.apple.com/es/shop/buy-mac/mac-pro'),

                          ('iPad Pro',
                           'http://store.storeimages.cdn-apple.com/4662/as-images.apple.com/is/image/AppleInc/aos/published/images/i/pa/ipad/pro/ipad-pro-201603-gallery1_GEO_ES?wid=2000&amp;hei=1536&amp;fmt=jpeg&amp;qlt=95&amp;op_sharpen=0&amp;resMode=bicub&amp;op_usm=0.5,0.5,0,0&amp;iccEmbed=0&amp;layer=comp&amp;.v=1473455675987',
                           'description0',
                           'http://www.apple.com/es/ipad-pro/', 'http://www.apple.com/es/shop/buy-ipad/ipad-pro'),
                          ('iPad Air 2',
                           'http://store.storeimages.cdn-apple.com/4662/as-images.apple.com/is/image/AppleInc/aos/published/images/i/pa/ipad/air/ipad-air-201410-gallery4_GEO_ES?wid=2000&amp;hei=1536&amp;fmt=jpeg&amp;qlt=95&amp;op_sharpen=0&amp;resMode=bicub&amp;op_usm=0.5,0.5,0,0&amp;iccEmbed=0&amp;layer=comp&amp;.v=1473967298447',
                           'description1',
                           'http://www.apple.com/es/ipad-air-2/', 'http://www.apple.com/es/shop/buy-ipad/ipad-air-2'),
                          ('iPad mini 4',
                           'http://store.storeimages.cdn-apple.com/4662/as-images.apple.com/is/image/AppleInc/aos/published/images/i/pa/ipad/mini/ipad-mini-4-201509-gallery4_GEO_ES?wid=2000&amp;hei=1536&amp;fmt=jpeg&amp;qlt=95&amp;op_sharpen=0&amp;resMode=bicub&amp;op_usm=0.5,0.5,0,0&amp;iccEmbed=0&amp;layer=comp&amp;.v=1474647599226',
                           'description2',
                           'http://www.apple.com/es/ipad-mini-4/', 'http://www.apple.com/es/shop/buy-ipad/ipad-mini-4'),

                          ('iPhone 7',
                           'http://images.apple.com/v/iphone/compare/e/images/compare/compare_iphone7_plus_black_large.jpg',
                           'description3',
                           'http://www.apple.com/es/iphone-7/', 'http://www.apple.com/es/shop/buy-iphone/iphone-7'),
                          ('iPhone 6s',
                           'http://images.apple.com/v/iphone/compare/e/images/compare/compare_iphone6s_plus_spacegray_large.jpg',
                           'description3',
                           'http://www.apple.com/es/iphone-6s/specs/', 'http://www.apple.com/es/shop/buy-iphone/iphone6s'),
                          ('iPhone SE',
                           'http://images.apple.com/v/iphone/compare/e/images/compare/compare_iphoneSE_spgray_large.jpg',
                           'description3',
                           'http://www.apple.com/es/iphone-se/', 'http://www.apple.com/es/shop/buy-iphone/iphone-se')
                      ])

        id_categories = c.execute('SELECT id_category FROM category_table').fetchall()
        id_products = c.execute('SELECT id_product FROM product_table').fetchall()

        c.executemany('INSERT INTO rel_category_product VALUES (?, ?, ?)',
                      [
                          (id_products[0][0], id_categories[0][0], 2),
                          (id_products[1][0], id_categories[0][0], 1),
                          (id_products[2][0], id_categories[0][0], 4),
                          (id_products[3][0], id_categories[0][0], 3),

                          (id_products[4][0], id_categories[1][0], 1),
                          (id_products[5][0], id_categories[1][0], 2),
                          (id_products[6][0], id_categories[1][0], 3),

                          (id_products[7][0], id_categories[2][0], 1),
                          (id_products[8][0], id_categories[2][0], 2),
                          (id_products[9][0], id_categories[2][0], 3),
                      ])

    conn_db.commit()
    c.close()

if __name__ == '__main__':
    populate()
    app.run(host='0.0.0.0', debug=True)
