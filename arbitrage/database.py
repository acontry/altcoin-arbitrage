
import peewee
import logging
import config


# Database initialization
if config.db_type == "sqlite":
    database = peewee.SqliteDatabase("trader_db.db", threadlocals=True)
elif config.db_type == "mysql":
    database = peewee.MySQLDatabase(config.db_name, unix_socket=config.db_unix_socket, user=config.db_username,
                                    passwd=config.db_password)
else:
    raise Exception("db_type must be sqlite or mysql")


# Models
class BaseModel(peewee.Model):
    class Meta:
        database = database


class MarketOrder(BaseModel):
    order_id = peewee.CharField(max_length=64)
    market = peewee.CharField(max_length=32)
    time_placed = peewee.DateTimeField()
    order_type = peewee.CharField(max_length=4)
    price = peewee.DecimalField(max_digits=12, decimal_places=8)
    amount = peewee.DecimalField(max_digits=18, decimal_places=8)
    has_executed = peewee.BooleanField(default=False)

    class Meta:
        order_by = ('-time_placed',)

# Test connection and create tables
if config.use_db is True:
    database.connect()
    database.close()
    logging.info("Logging to %s database", config.db_type)
    # Create table if it doesn't exist
    MarketOrder.create_table(fail_silently=True)


def place_order(order_id, market, time_placed, order_type, order_price, order_amount):
    if config.use_db is False:
        pass
    database.connect()
    MarketOrder.create(order_id=order_id, market=market, time_placed=time_placed, order_type=order_type,
                       price=order_price, amount=order_amount)
    database.close()


def order_completed(market, order_ids):
    if config.use_db is False:
        pass
    database.connect()
    update_orders = MarketOrder.update(has_executed=True).\
        where((MarketOrder.market == market) & (MarketOrder.order_id << order_ids))
    update_orders.execute()
    database.close()


