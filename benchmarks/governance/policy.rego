package comparative
import rego.v1

# Authentication and durable effect lookup occur in the application. Policy
# consumes destination-owned state inside its SQLite writer transaction.
default allow := false
allow if {
    input.generation == input.state.generation
    input.generation == input.state.grant_generation
    input.policy == input.state.policy
    input.target == input.state.target
    input.state.revoked == false
    input.state.consumed < input.state.max_effects
    input.now < input.state.expires_at
    input.verifier_valid == true
    input.state.credential == input.state.provisioned_credential
    input.state.dependency == input.state.provisioned_dependency
    input.state.grants == input.state.provisioned_grants
}
