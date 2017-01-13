const gHosts = "var/hosts.json"

function Date2String( date, seconds=false )
{
    var month  = ( "0" + (date.getMonth()+1) ).slice(-2);
    var day    = ( "0" +  date.getDate()     ).slice(-2);
    var hour   = ( "0" +  date.getHours()    ).slice(-2);
    var minute = ( "0" +  date.getMinutes()  ).slice(-2);
    ret = date.getFullYear() + '-' + month + '-' + day + ' ' + hour + ':' + minute;
    if( seconds )
    {
        var second = ( "0" +  date.getSeconds() ).slice(-2);
        ret += ':' + second;
    }
    return ret;
}

function LoadData()
{
    d = new Date();
    fetch( gHosts + "?d=" + d.getMilliseconds() ).then( function(response)
    {
        return response.json().then( function(json)
        {
            var table = document.getElementById( "host-table" );
            table.innerHTML = "<tr><th>Host</th><th>Status</th><th>Last change</th></tr>";
            for( var i=0; i<json['hosts'].length; ++i )
            {
                var status = json['hosts'][i]['online'] ? "online" : "offline";
                var last_change = new Date( json['hosts'][i]['lastchange'] );
                var html = '<tr><td>' + json['hosts'][i]['name'] + '</td><td class="' + status + '">' + status + '</td><td>' + Date2String( last_change ) + '</td></tr>';
                table.innerHTML += html;
            }

            var div = document.getElementById( "updated-div" );
            div.innerHTML = "Last updated: " + Date2String( new Date( json['updated'] ) );
        });
    });
}

window.addEventListener( 'load', function()
{
    LoadData();
    setInterval( LoadData, 30000 );
});
