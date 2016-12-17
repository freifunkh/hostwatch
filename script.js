const gHosts = "var/hosts.json"

function Date2String( date )
{
    var month  = ( "0" + date.getMonth()   ).slice(-2);
    var day    = ( "0" + date.getDate()    ).slice(-2);
    var hour   = ( "0" + date.getHours()   ).slice(-2);
    var minute = ( "0" + date.getMinutes() ).slice(-2);
    return date.getFullYear() + '-' + month + '-' + day + ' ' + hour + ':' + minute;
}

function LoadData()
{
    d = new Date();
    fetch( gHosts + "?d=" + d.getSeconds() ).then( function(response)
    {
        response.json().then( function(data)
        {  
            var table = document.getElementById( "host-table" );
            table.innerHTML = "<tr><th>Host</th><th>Status</th><th>Last change</th></tr>";
            for( var i=0; i<data.length; ++i )
            {
                var status = data[i]['online'] ? "online" : "offline";
                var last_change = new Date( data[i]['lastchange'] );
                var html = "<tr><td>" + data[i]['name'] + "</td><td>" + status + "</td><td>" + Date2String( last_change ) + "</td></tr>";
                table.innerHTML += html;
            }
        });
    });
}

window.addEventListener( 'load', function()
{
    LoadData();
    setInterval( LoadData, 30000 );
});
