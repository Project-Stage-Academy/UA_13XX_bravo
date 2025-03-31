from rest_framework import serializers

from projects.models import Project


class ProjectListSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=[choice[0] for choice in Project._meta.get_field("status").choices],
        error_messages={
            "invalid_choice": "Invalid company status. Choose from: {}".format(
                ", ".join(
                    [choice[0] for choice in Project._meta.get_field("status").choices]
                )
            )
        },
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "status",
            "information",
            "required_funding",
            "raised_amount",
            "company",
        )


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=[choice[0] for choice in Project._meta.get_field("status").choices],
        error_messages={
            "invalid_choice": "Invalid company status. Choose from: {}".format(
                ", ".join(
                    [choice[0] for choice in Project._meta.get_field("status").choices]
                )
            )
        },
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "status",
            "information",
            "required_funding",
            "raised_amount",
        )
        extra_kwargs = {"company": {"required": False}}

    def validate(self, attrs):
        required_funding = attrs.get("required_funding")
        raised_amount = attrs.get("raised_amount")

        if required_funding < 0:
            raise serializers.ValidationError("Required funding cannot be negative.")
        if raised_amount < 0:
            raise serializers.ValidationError("Raised amount cannot be negative.")
        if raised_amount > required_funding:
            raise serializers.ValidationError(
                "Raised amount cannot be greater than required funding."
            )

        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get("request")
        company_id = request.auth.get("company_id")

        if not company_id:
            raise serializers.ValidationError("Company ID is missing in the token.")

        validated_data["company_id"] = company_id
        return super().create(validated_data)
