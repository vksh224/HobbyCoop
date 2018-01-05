'use strict';


/**
*https://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs
**/

angular.module('h4hApp')
    .factory('UserService', function($http,$q, $location, $cookies) {
        return {
            setUserId : function(emailId, password){
                var deferred = $q.defer();
                console.log("Here in sign In modal " + emailId+" "+ password);
                var dataObj = {
                            email    : emailId,
                            password : password
                    };
                    var res = $http.post(server_url + 'login', dataObj);
                    res.success(function(data, status, headers, config) {
                         deferred.resolve(data);
                         //console.log(data);
                        //$scope.message = data;
                        $cookies.put('userId', data.user_id);
                        console.log("At login, the path is: ");
                        console.log($location);
                        $location.path('/myAccount');
                    });
                    res.error(function(data, status, headers, config) {
                        deferred.reject(data);
                    });
                    //REMOVE BELOW TWO LINES

                    return deferred.promise;
            },
            getUserId : function(){
                var id = $cookies.get('userId');
                return Number(id);
            },
            logout: function() {
              $cookies.put('userId', null);
              $location.path('#/');
            }
        };
    });
