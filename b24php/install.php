<?php
require_once(__DIR__ . '/crest.php');

$result = CRest::installApp();
if ($result['rest_only'] === false):?>
    <head>
        <title>Title</title>
        <script src="//api.bitrix24.com/api/v1/"></script>
        <?php if ($result['install']): ?>
            <script>
                BX24.init(function () {
                    BX24.installFinish();
                });
            </script>
        <?php endif; ?>
    </head>
    <body>
    <?php if ($result['install']): ?>
        installation has been finished
    <?php else: ?>
        installation error
    <?php endif; ?>
    </body>
<?php endif;