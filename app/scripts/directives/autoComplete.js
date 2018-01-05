'use strict';



angular.module('h4hApp')
.directive('autoComplete', function ($http) {
    return {
        restrict: 'A',
        scope: {
            url : '@',
            itemsList:'=itemsList',
            ngModel:'='
        },
        controller: ['$scope', function($scope){
          // And here you can access your data
          console.log("here " + $scope.itemsList);
        }],
        link: function(scope, element, attrs) {
           // scope.$watch('itemsList', function(newValue, oldValue) { 
           //      console.log(newValue)
           //      scope.itemsList = newValue;
           //  }, true);
           // console.log(scope.itemsList);
            console.log("there "+scope.itemsList);
             element.autocomplete({
           //      // source: function(request, response){
           //      //    $http({
           //      //           method: 'GET',
           //      //           url: 'scripts/controllers/lentItems.json'
           //      //         }).success(function(data){
           //      //         console.log(data);
           //      //         response(data);
           //      //     })
           //      // },
                source:scope.itemsList,
                select: function (event, selectedItem) {
                    // Do something with the selected item, e.g. 
                    scope.ngModel= selectedItem.item.value;
                    //console.log(selectedItem);

                    scope.$apply();
                    //event.preventDefault();
                },
                 minLength: 1
            })
        }
    }
});