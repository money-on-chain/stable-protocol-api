# exit as soon as an error happen
set -e

usage() { echo "Usage: $0 -e <environment> -i <aws id> -r <aws region>" 1>&2; exit 1; }

while getopts ":e:i:r:" o; do
    case "${o}" in
        e)
            e=${OPTARG}
            (( e=="testnet" ||  e=="mainnet")) || usage
            case $e in
                testnet)
                    ENV=$e
                    ;;
                mainnet)
                    ENV=$e
                    ;;
                *)
                    usage
                    ;;
            esac
            ;;
        i)
            i=${OPTARG}
            AWS_ID=$i
            ;;
        r)
            r=${OPTARG}
            AWS_REGION=$r
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${e}" ] || [ -z "${i}" ] || [ -z "${r}" ]; then
    usage
fi

docker image build -t nginx_operations_$ENV -f ./Dockerfile.nginx .

echo "Build done!"

docker tag nginx_operations_$ENV:latest $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nginx_operations_$ENV:latest

docker push $AWS_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nginx_operations_$ENV:latest

echo "finish done!"