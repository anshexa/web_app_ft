# coding=utf-8
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from flask import render_template, request, url_for

from app import app
import json

from app.models import Category, Product
from app.pagination import Pagination


def url_for_other_page(page, prefix):
    args = request.view_args.copy()
    args[prefix] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals.update(url_for_other_page=url_for_other_page)


@app.route('/', methods=['GET', 'POST'])
@app.route('/sku', methods=['GET', 'POST'])
@app.route('/sku/page/<int:page>')
@app.route('/cat/<string:hash>', methods=['GET', 'POST'])
@app.route('/cat/<string:hash>/page/<int:page>', methods=['GET', 'POST'])
def sku(page=1, hash=''):
    total = get_total_sku(hash)
    per_page = 10
    offset = ((int(page) - 1) * per_page)
    pagination_sku = extr_sku_from_bd(offset=offset, limit=per_page, hash=hash)
    # Display a 409 not found page for an out of bounds request
    if not pagination_sku and page != 1:
        return render_template('errors/409.html', errmsg="Requested page out of bounds"), 409
    pagination = Pagination(page, per_page, total)
    cat = extr_cat_info()
    prefix = 'page'
    return render_template('sku.html',
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           result=pagination_sku,
                           cat=cat,
                           prefix=prefix)


#  страница с инфо о продукте
@app.route('/product/<string:sku>', methods=['GET', 'POST'])
def info(sku):
    prod_info = extr_prod_info(sku)
    return render_template("product.html",
                           prod=prod_info)


# запрос записей из бд (дерево Nested Sets)
def extr_sku_from_bd(offset, limit, hash):
    sku_list = []
    if len(hash) > 0:
        # запрашиваем параметры для запроса
        # определяем границы потомков для данного хеш и id дерева
        query_list = Category.query.with_entities(Category.left, Category.right, Category.tree_id).filter(
            Category.hash == hash).all()
        lft = query_list[0][0]
        rgt = query_list[0][1]
        tree_id = query_list[0][2]
        # определяем id категорий всех потомков
        id_list = Category.query.with_entities(Category.id).filter(Category.left >= lft, Category.right <= rgt,
                                                                   Category.tree_id == tree_id).all()
        sku_list_tup = Product.query.with_entities(Product.sku).filter(Product.id_cat.in_(id_list)).offset(
            offset).limit(limit).all()
        for sku in sku_list_tup:
            sku_list.append(str(sku[0]))
    else:
        # выбрать все sku из табл (от и сколько)
        sku_list_tup = Product.query.with_entities(Product.sku).offset(offset).limit(limit)
        for sku in sku_list_tup:
            sku_list.append(str(sku[0]))
    return sku_list


# выбор из бд категорий (дерево Nested Sets)
def extr_cat_info():
    nodes = {}
    nodes['children'] = []
    # запрос узлов 1го уровня (без родителей)
    categories = Category.query.filter(Category.level == 1)

    def cat_to_json(item):
        return {
            'id': item.id,
            'name': item.name,
            'hash': item.hash
        }

    for item in categories:
        nodes['children'].append(item.drilldown_tree(json=True, json_fields=cat_to_json)[0])
    return nodes


# выбор из бд инфо о товаре
def extr_prod_info(sku):
    # выбрать строку из табл с определенным sku
    prod_list = Product.query.filter(Product.sku == sku).first()

    category = prod_list.category_f
    name = prod_list.name
    title = prod_list.title
    specifications = json.loads(prod_list.specifications)
    price = prod_list.price
    priceCurrency = prod_list.priceCurrency
    url = prod_list.url
    details = prod_list.details
    imgs = json.loads(prod_list.imgs)
    desc = prod_list.descr

    prod_info = {'category': category, 'name': name, 'title': title,
                 'specifications': specifications, 'price': price, 'priceCurrency': priceCurrency, 'url': url,
                 'details': details, 'imgs': imgs, 'desc': desc}
    return prod_info


# количество записей в бд (дерево Nested Sets)
def get_total_sku(hash):
    if len(hash) > 0:
        # запрашиваем параметры для запроса
        # определяем границы потомков для данного хеш
        query_list = Category.query.with_entities(Category.left, Category.right, Category.tree_id).filter(
            Category.hash == hash).all()
        lft = query_list[0][0]
        rgt = query_list[0][1]
        tree_id = query_list[0][2]
        # определяем id категорий всех потомков
        id_list = Category.query.with_entities(Category.id).filter(Category.left >= lft, Category.right <= rgt,
                                                                   Category.tree_id == tree_id).all()
        # находим в таблице товаров количество товаров с данными id
        total = Product.query.filter(Product.id_cat.in_(id_list)).count()
    else:
        # количество записей в табл товары
        total = Product.query.count()
    return total
