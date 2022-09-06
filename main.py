from config import Config
import time
from influxdb_client import InfluxDBClient
from discord_webhook import DiscordWebhook, DiscordEmbed
import logging
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

if Config.UPLOAD_GRAPHS=='true':
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    import json

Config = Config()


if Config.ENV == "DEV":
    loop_timer=60
else:
    loop_timer=86400

client = InfluxDBClient(url=Config.INFLUX_ADDR, token=Config.INFLUX_TOKEN, org=Config.INFLUX_ORG)

query_api = client.query_api()
bucketname = Config.INFLUX_BUCKET
org = Config.INFLUX_ORG

person = (Config.PERSON)
namelower = person.lower
measurement = Config.MEASUREMENT
field = Config.FIELD


# Cloudinary for graph hosting
if Config.UPLOAD_GRAPHS=='true':
    cloudinary.config(
    cloud_name = Config.CLOUDINARY_CLOUD_NAME,
    api_key = Config.CLOUDINARY_API_KEY,
    api_secret = Config.CLOUDINARY_API_SECRET,
    secure=True
    )


def get_latest_result_from_influx_table(influxtable):
    results = []
    for table in influxtable:
        for record in table.records:
            logging.info(record)
            results.append((record.get_field(), record.get_value()))
    data = results[0][1]
    return data


def get_updates_and_do_discord_alert(graphurl=None):

    logging.info("Getting portfolio now")

    query = 'from(bucket: "fromdevices")\
    |> range(start: -10m)\
    |> filter(fn: (r) => r["_measurement"] == "' + measurement + '")\
    |> filter(fn: (r) => r["_field"] == "' + field + '")\
    |> last()\
    |> yield(name: "last")'
    result = query_api.query(org=org, query=query)
    logging.debug(result)
    portfolio_today = get_latest_result_from_influx_table(result)    
    logging.debug(person + ' portfolio today: ' + str(portfolio_today))


    logging.info("Getting portfolio yesterday")
    
    query = 'from(bucket: "fromdevices")\
    |> range(start: -25h, stop: -24h)\
    |> filter(fn: (r) => r["_measurement"] == "' + measurement + '")\
    |> filter(fn: (r) => r["_field"] == "' + field + '")\
    |> last()\
    |> yield(name: "last")'
    result = query_api.query(org=org, query=query)
    logging.debug(result)
    portfolio_yesterday = get_latest_result_from_influx_table(result)
    logging.debug(person + ' portfolio yesterday: ' + str(portfolio_yesterday))


    diff = portfolio_today - portfolio_yesterday

    # get percentage change
    percentage = diff / portfolio_today * 100
    percentage = "%.2f" % percentage
    percentage = (percentage + '%')

    portfolio_today = "%.2f" % portfolio_today
    portfolio_yesterday = "%.2f" % portfolio_yesterday
    diff = "%.2f" % diff

    logging.info(person + " portfolio is £{}".format(portfolio_today))
    logging.info("yesterdays value is: £" + str(portfolio_yesterday))
    logging.info("difference is: £" + str(diff))
    logging.info("difference in percentage is: " + percentage)

    if float(diff) > 0:
        direction = "Up"
        colour = '00FF00'
        icon = Config.EMOJIUP
    else:
        direction = "Down"
        colour= 'FF0000'
        icon = Config.EMOJIDOWN

    graphgoes = "Graph goes " + direction + " " + icon
    logging.info(graphgoes)


    webhook = DiscordWebhook(url=Config.DISCORDWEBHOOK)
    
    embed = DiscordEmbed(title='Crypto Stash Update', description=graphgoes, color=colour)
    embed.add_embed_field(name=person+'\'s Stash ', value="£"+str(portfolio_today), inline=False)
    embed.add_embed_field(name=person+'\'s Stash Yesterday', value="£"+str(portfolio_yesterday), inline=False)
    embed.add_embed_field(name='Daily Change ', value="£"+str(diff) + " (" + str(percentage) + ")")
    if graphurl != None:
        logging.info("Got a graph to show")
        embed.set_image(url=graphurl)
    else:
        logging.info("No graph to show")
    webhook.add_embed(embed)

    if Config.SENDWEBHOOK == "true":
        logging.info("Sending webhook to discord")
        response = webhook.execute()
    else:
        logging.info("SENDWEBHOOK is false, not sending anything")


def get_portfolio_graph(myrange='30d'):

    query = 'from(bucket: "fromdevices")\
    |> range(start: -'+ myrange +')\
    |> filter(fn: (r) => r["_measurement"] == "' + measurement + '")\
    |> filter(fn: (r) => r["_field"] == "' + field + '")\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    result = query_api.query_data_frame(org=org, query=query)
    logging.debug(result)

    result.plot(kind='line', x='_time', y='holdings_gbp',legend=None)

    plt.xlabel('Date')
    plt.ylabel('Stash')
    plt.title('Portfolio ('+ myrange + ')' )
    filename = 'output_'+myrange+'.png'
    plt.savefig(filename)

    # upload - cloudinary free account appears to be ok
    if Config.UPLOAD_GRAPHS=='true':
        logging.info("Upload graphs is set to true... attempting to upload now.")
        result = cloudinary.uploader.upload(filename, folder='portfolio_graphs')
        logging.debug(result)
        graphurl = result['url']
        logging.info('Graph URL is: ' + graphurl)
    else:
        graphurl = None
    return graphurl


def main():
    logging.basicConfig(format=Config.LOG_FORMAT ,level=Config.LOG_LEVEL)
    logging.info('Started application {} in {}'.format(Config.APPNAME, Config.ENV))

    if Config.LOOPMODE == "true":

        logging.info('Loop timer: {}'.format(loop_timer))

        while True:
            # the main bit
            logging.info("Getting latest updates ...")
            graphurl = get_portfolio_graph('30d')
            get_updates_and_do_discord_alert(graphurl)

            # loop delay
            logging.info("Waiting for next run.")
            time.sleep(loop_timer)

    else:
        logging.info('Started in non-looping mode')
        logging.info("Getting latest updates ...")
        graphurl = get_portfolio_graph('30d')
        get_updates_and_do_discord_alert(graphurl)

        exit(0)

if __name__ == '__main__':
    main()
