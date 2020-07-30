$currentThread = [System.Threading.Thread]::CurrentThread
$culture = [CultureInfo]::InvariantCulture.Clone()
$culture.DateTimeFormat.ShortDatePattern = 'yyyy-MM-dd'
$currentThread.CurrentCulture = $culture
$currentThread.CurrentUICulture = $culture